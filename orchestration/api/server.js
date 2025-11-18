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
      
      case 'cve_detected':
        response = await handleCVEEvent(data);
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

// CVE information endpoint (proxy to AI API)
app.get('/cve/:cveId', async (req, res) => {
  try {
    const { cveId } = req.params;
    logger.info(`Fetching CVE info for: ${cveId}`);
    
    const response = await axios.get(`${AI_API_URL}/cveinfo?cve=${cveId}`, { timeout: 10000 });
    res.json(response.data);
  } catch (error) {
    logger.error(`CVE fetch error: ${error.message}`);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

// Event handlers
async function handleAnomalyEvent(data) {
  logger.info('Handling anomaly event');
  orchestrationEvents.inc({ type: 'anomaly_handled' });
  
  // Check if CVE is involved
  if (data.cve_detected && data.cve_ids) {
    logger.warn(`CVE detected in anomaly: ${data.cve_ids}`);
    return await handleCVEEvent(data);
  }
  
  // Forward to AI for deeper analysis
  try {
    await axios.post(`${AI_API_URL}/analyze`, data);
  } catch (error) {
    logger.error(`Failed to forward to AI: ${error.message}`);
  }

  return { status: 'processed', action: 'anomaly_logged' };
}

async function handleCVEEvent(data) {
  logger.warn('Handling CVE detection event');
  orchestrationEvents.inc({ type: 'cve_detected' });
  
  const cveIds = data.cve_ids || [];
  
  if (cveIds.length === 0) {
    return { status: 'ignored', message: 'No CVE IDs provided' };
  }

  // Fetch CVE details for each detected CVE
  const cveDetails = [];
  for (const cveId of cveIds) {
    try {
      const response = await axios.get(`${AI_API_URL}/cveinfo?cve=${cveId}`, { timeout: 5000 });
      cveDetails.push(response.data);
    } catch (error) {
      logger.error(`Failed to fetch CVE info for ${cveId}: ${error.message}`);
    }
  }

  if (cveDetails.length === 0) {
    logger.warn('Failed to fetch CVE details, proceeding with default handling');
    return { status: 'partial', message: 'CVE enrichment failed' };
  }

  // Determine maximum CVSS score
  const cvssScores = cveDetails
    .filter(cve => cve.cvss_base_score)
    .map(cve => cve.cvss_base_score);
  
  const maxCVSS = cvssScores.length > 0 ? Math.max(...cvssScores) : 0;
  
  logger.info(`CVE detected with max CVSS score: ${maxCVSS}`);

  // Adaptive response based on CVSS severity
  const actions = [];
  
  if (maxCVSS >= 9.0) {
    // CRITICAL severity (CVSS >= 9.0)
    logger.error(`CRITICAL CVE detected! CVSS: ${maxCVSS}`);
    
    actions.push({
      type: 'deploy_specialized_honeypot',
      priority: 'critical',
      reason: `Critical CVE detected with CVSS ${maxCVSS}`,
      parameters: {
        honeypot_type: 'high_interaction',
        isolation_level: 'maximum',
        logging_level: 'verbose'
      }
    });
    
    actions.push({
      type: 'increase_monitoring',
      priority: 'critical',
      parameters: {
        monitoring_level: 'maximum',
        alert_threshold: 'low',
        session_recording: true
      }
    });
    
    actions.push({
      type: 'redirect_attacker',
      priority: 'critical',
      parameters: {
        target: 'isolated_decoy',
        instrumentation: 'full'
      }
    });

    // Trigger infrastructure update
    try {
      await triggerTerraformUpdate({
        severity: 'critical',
        actions: actions,
        cve_info: cveDetails
      });
    } catch (error) {
      logger.error(`Failed to trigger Terraform update: ${error.message}`);
    }

  } else if (maxCVSS >= 7.0) {
    // HIGH severity (7.0 <= CVSS < 9.0)
    logger.warn(`HIGH severity CVE detected! CVSS: ${maxCVSS}`);
    
    actions.push({
      type: 'scale_honeypots',
      priority: 'high',
      reason: `High severity CVE detected with CVSS ${maxCVSS}`,
      parameters: {
        scale_factor: 1.5,
        honeypot_type: 'medium_interaction'
      }
    });
    
    actions.push({
      type: 'increase_monitoring',
      priority: 'high',
      parameters: {
        monitoring_level: 'elevated',
        alert_threshold: 'medium'
      }
    });

    // Medium-level adaptive response
    try {
      await triggerTerraformUpdate({
        severity: 'high',
        actions: actions,
        cve_info: cveDetails
      });
    } catch (error) {
      logger.error(`Failed to trigger infrastructure update: ${error.message}`);
    }

  } else if (maxCVSS >= 4.0) {
    // MEDIUM severity
    logger.info(`MEDIUM severity CVE detected. CVSS: ${maxCVSS}`);
    
    actions.push({
      type: 'log_and_monitor',
      priority: 'medium',
      reason: `Medium severity CVE detected with CVSS ${maxCVSS}`,
      parameters: {
        enhanced_logging: true
      }
    });
  } else {
    // LOW/NONE severity - default behavior
    logger.info(`LOW severity CVE detected. CVSS: ${maxCVSS}`);
    
    actions.push({
      type: 'log',
      priority: 'low',
      reason: `Low severity CVE detected with CVSS ${maxCVSS}`
    });
  }

  return {
    status: 'processed',
    cve_count: cveDetails.length,
    max_cvss_score: maxCVSS,
    actions: actions,
    cve_details: cveDetails.map(cve => ({
      cve_id: cve.cve_id,
      cvss_score: cve.cvss_base_score,
      severity: cve.cvss_severity
    }))
  };
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
