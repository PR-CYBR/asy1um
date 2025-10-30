const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const cors = require('cors');
const winston = require('winston');
const { register, Counter, Gauge, Histogram } = require('prom-client');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Prometheus metrics
const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status']
});

const orchestrationEvents = new Counter({
  name: 'orchestration_events_total',
  help: 'Total orchestration events processed',
  labelNames: ['type']
});

const infrastructureState = new Gauge({
  name: 'infrastructure_state',
  help: 'Current infrastructure state',
  labelNames: ['component']
});

const eventProcessingDuration = new Histogram({
  name: 'event_processing_duration_seconds',
  help: 'Duration of event processing',
  labelNames: ['event_type']
});

// Configuration
const AI_API_URL = process.env.AI_API_URL || 'http://ai-api:8000';
const TERRAFORM_STATE_PATH = process.env.TERRAFORM_STATE_PATH || '../terraform/state.json';

// Routes
app.get('/', (req, res) => {
  res.json({
    service: 'Project Asylum Orchestration API',
    version: '1.0.0',
    status: 'operational'
  });
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      ai_api: 'checking...',
      terraform: 'checking...'
    }
  });
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// Event handling endpoint
app.post('/events', async (req, res) => {
  const timer = eventProcessingDuration.startTimer();
  const { type, data, source } = req.body;

  try {
    logger.info(`Received event: ${type} from ${source}`);
    orchestrationEvents.inc({ type });

    let response;

    switch (type) {
      case 'anomaly_detected':
        response = await handleAnomalyEvent(data);
        break;
      
      case 'threshold_exceeded':
        response = await handleThresholdEvent(data);
        break;
      
      case 'infrastructure_drift':
        response = await handleDriftEvent(data);
        break;
      
      case 'honeypot_compromised':
        response = await handleCompromiseEvent(data);
        break;
      
      default:
        response = { status: 'ignored', message: `Unknown event type: ${type}` };
    }

    timer({ event_type: type });
    res.json(response);
  } catch (error) {
    logger.error(`Error processing event: ${error.message}`);
    timer({ event_type: 'error' });
    res.status(500).json({ error: error.message });
  }
});

// AI integration endpoint
app.post('/analyze', async (req, res) => {
  try {
    const { features } = req.body;
    
    logger.info('Forwarding analysis request to AI API');
    
    const response = await axios.post(`${AI_API_URL}/analyze`, {
      features,
      metadata: {
        timestamp: new Date().toISOString(),
        source: 'orchestration'
      }
    });

    const recommendations = response.data;
    
    // Process recommendations
    if (recommendations.severity === 'critical') {
      logger.warn('Critical severity detected, triggering infrastructure update');
      await triggerTerraformUpdate(recommendations);
    }

    res.json(recommendations);
  } catch (error) {
    logger.error(`AI analysis error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// Terraform integration endpoint
app.post('/infrastructure/update', async (req, res) => {
  try {
    const { action, parameters } = req.body;
    
    logger.info(`Infrastructure update requested: ${action}`);
    
    // In production, this would trigger actual Terraform apply
    // For now, simulate the update
    const result = {
      status: 'planned',
      action,
      parameters,
      timestamp: new Date().toISOString(),
      message: 'Terraform plan created. Review and apply manually or via CI/CD.'
    };

    infrastructureState.set({ component: 'terraform' }, 1);
    
    res.json(result);
  } catch (error) {
    logger.error(`Infrastructure update error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// Get current state
app.get('/state', (req, res) => {
  // In production, read from actual state files
  res.json({
    infrastructure: {
      node_count: 3,
      environment: 'dev',
      last_update: new Date().toISOString()
    },
    ai: {
      model_loaded: true,
      last_training: new Date().toISOString()
    },
    monitoring: {
      prometheus: 'healthy',
      grafana: 'healthy',
      elasticsearch: 'healthy'
    }
  });
});

// Event handlers
async function handleAnomalyEvent(data) {
  logger.info('Handling anomaly event');
  orchestrationEvents.inc({ type: 'anomaly_handled' });
  
  // Forward to AI for deeper analysis
  try {
    await axios.post(`${AI_API_URL}/analyze`, data);
  } catch (error) {
    logger.error(`Failed to forward to AI: ${error.message}`);
  }

  return { status: 'processed', action: 'anomaly_logged' };
}

async function handleThresholdEvent(data) {
  logger.warn('Threshold exceeded, considering infrastructure scaling');
  
  if (data.anomaly_rate > 0.5) {
    return await triggerTerraformUpdate({
      actions: [{
        type: 'scale_up',
        parameter: 'node_count',
        suggested_value: data.current_nodes + 2
      }]
    });
  }

  return { status: 'monitored', action: 'none_required' };
}

async function handleDriftEvent(data) {
  logger.warn('Infrastructure drift detected');
  return { status: 'drift_detected', action: 'manual_review_required' };
}

async function handleCompromiseEvent(data) {
  logger.error('Honeypot compromise detected');
  orchestrationEvents.inc({ type: 'compromise_detected' });
  
  // Rotate honeypot configurations
  return {
    status: 'handled',
    actions: ['rotate_honeypots', 'alert_team']
  };
}

async function triggerTerraformUpdate(recommendations) {
  logger.info('Triggering Terraform update based on recommendations');
  
  // In production, this would:
  // 1. Update terraform variables
  // 2. Run terraform plan
  // 3. Submit for approval or auto-apply
  
  return {
    status: 'terraform_update_planned',
    recommendations,
    message: 'Update planned. Awaiting approval.'
  };
}

// Start server
app.listen(PORT, () => {
  logger.info(`Orchestration API listening on port ${PORT}`);
  console.log(`Orchestration API running on http://localhost:${PORT}`);
});

module.exports = app;
