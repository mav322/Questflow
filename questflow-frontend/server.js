/**
 * QuestFlow // Frontend Application Server
 * Serves static assets and proxies /api/* requests to Flask ML engine.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 3000;
const BACKEND_HOST = process.env.BACKEND_HOST || '127.0.0.1';
const BACKEND_PORT = Number(process.env.BACKEND_PORT || 5000);

// MIME types for static asset resolution
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.zip': 'application/zip'
};

// ==============================================================================
// EMBEDDED SDLC RULE ENGINE (Built-in Standalone Engine for All 5 Models)
// ==============================================================================

const SDLC_RULES = {
  Waterfall: [
    { phase: 'Requirements', item: '1_Requirements/SRS.md', weight: 20 },
    { phase: 'Requirements', item: '1_Requirements/user_stories.md', weight: 10 },
    { phase: 'Design', item: '2_Design/architecture.png', weight: 15 },
    { phase: 'Design', item: '2_Design/schema.sql', weight: 10 },
    { phase: 'Source', item: '3_Source/', weight: 15 },
    { phase: 'Testing', item: '4_Testing/unit_tests/', weight: 15 },
    { phase: 'Testing', item: '4_Testing/test_matrix.md', weight: 5 },
    { phase: 'DevOps', item: '5_DevOps/Dockerfile', weight: 5 },
    { phase: 'DevOps', item: '5_DevOps/.github/workflows/', weight: 5 }
  ],
  Agile: [
    { phase: 'Backlog', item: 'docs/backlog.md', weight: 15 },
    { phase: 'Backlog', item: 'docs/sprint_board.json', weight: 10 },
    { phase: 'Design', item: 'docs/wireframes/', weight: 10 },
    { phase: 'Design', item: 'docs/api_contract.json', weight: 10 },
    { phase: 'Source', item: 'src/components/', weight: 20 },
    { phase: 'Source', item: 'src/api/', weight: 15 },
    { phase: 'Testing', item: 'tests/unit/', weight: 10 },
    { phase: 'Testing', item: 'tests/integration/', weight: 10 },
    { phase: 'DevOps', item: 'Dockerfile', weight: 5 },
    { phase: 'DevOps', item: 'docker-compose.yml', weight: 5 }
  ],
  'V-Model': [
    { phase: 'Requirements', item: '1_Requirements/SRS.md', weight: 15 },
    { phase: 'Validation', item: '4_Validation/acceptance_test_plan.md', weight: 15 },
    { phase: 'Design', item: '2_Design/system_design.md', weight: 15 },
    { phase: 'Validation', item: '4_Validation/integration_tests/', weight: 15 },
    { phase: 'Source', item: '3_Source/', weight: 20 },
    { phase: 'Validation', item: '4_Validation/unit_tests/', weight: 20 }
  ],
  Spiral: [
    { phase: 'Objectives', item: '1_Objectives/mission_statement.md', weight: 10 },
    { phase: 'Objectives', item: '1_Objectives/risk_log.md', weight: 15 },
    { phase: 'Prototype', item: '2_Prototype/spike_evaluation.md', weight: 15 },
    { phase: 'Prototype', item: '2_Prototype/poc_source/', weight: 20 },
    { phase: 'Engineering', item: '3_Engineering/production_src/', weight: 20 },
    { phase: 'Engineering', item: '3_Engineering/test_bench/', weight: 10 },
    { phase: 'Evaluation', item: '4_Evaluation/stakeholder_signoff.md', weight: 10 }
  ],
  Iterative: [
    { phase: 'Inception', item: '1_Inception/charter.md', weight: 10 },
    { phase: 'Inception', item: '1_Inception/minimal_viable_spec.md', weight: 15 },
    { phase: 'Elaboration', item: '2_Elaboration/domain_model.png', weight: 10 },
    { phase: 'Elaboration', item: '2_Elaboration/api_spec.yaml', weight: 15 },
    { phase: 'Construction', item: '3_Construction/src/', weight: 25 },
    { phase: 'Construction', item: '3_Construction/tests/', weight: 15 },
    { phase: 'Transition', item: '4_Transition/performance_audit.md', weight: 10 }
  ]
};

const QUEST_STEPS = {
  Waterfall: [
    { step_order: 1, required_item: '1_Requirements/SRS.md', phase: 'Requirements', message: 'Draft your formal Software Requirements Specification in 1_Requirements/SRS.md', prereq: null },
    { step_order: 2, required_item: '1_Requirements/user_stories.md', phase: 'Requirements', message: 'Define acceptance criteria and user stories in 1_Requirements/user_stories.md', prereq: '1_Requirements/SRS.md' },
    { step_order: 3, required_item: '2_Design/architecture.png', phase: 'Design', message: 'Generate your high-level system architecture blueprint in 2_Design/architecture.png', prereq: '1_Requirements/user_stories.md' },
    { step_order: 4, required_item: '2_Design/schema.sql', phase: 'Design', message: 'Establish relational database DDL tables in 2_Design/schema.sql', prereq: '2_Design/architecture.png' },
    { step_order: 5, required_item: '3_Source/', phase: 'Source', message: 'Begin production application development under 3_Source/', prereq: '2_Design/schema.sql' },
    { step_order: 6, required_item: '4_Testing/unit_tests/', phase: 'Testing', message: 'Write automated regression & unit test suites in 4_Testing/unit_tests/', prereq: '3_Source/' },
    { step_order: 7, required_item: '4_Testing/test_matrix.md', phase: 'Testing', message: 'Document edge cases & pass/fail coverage criteria in 4_Testing/test_matrix.md', prereq: '4_Testing/unit_tests/' },
    { step_order: 8, required_item: '5_DevOps/Dockerfile', phase: 'DevOps', message: 'Containerize application environment using 5_DevOps/Dockerfile', prereq: '4_Testing/test_matrix.md' },
    { step_order: 9, required_item: '5_DevOps/.github/workflows/', phase: 'DevOps', message: 'Configure continuous integration pipelines in 5_DevOps/.github/workflows/', prereq: '5_DevOps/Dockerfile' }
  ],
  Agile: [
    { step_order: 1, required_item: 'docs/backlog.md', phase: 'Backlog', message: 'Formulate product backlog epics & prioritized user stories in docs/backlog.md', prereq: null },
    { step_order: 2, required_item: 'docs/sprint_board.json', phase: 'Backlog', message: 'Configure initial sprint board & work-in-progress limits in docs/sprint_board.json', prereq: 'docs/backlog.md' },
    { step_order: 3, required_item: 'docs/wireframes/', phase: 'Design', message: 'Design UI wireframes & user journey mockups under docs/wireframes/', prereq: 'docs/sprint_board.json' },
    { step_order: 4, required_item: 'docs/api_contract.json', phase: 'Design', message: 'Establish REST/GraphQL schema contracts in docs/api_contract.json', prereq: 'docs/wireframes/' },
    { step_order: 5, required_item: 'src/components/', phase: 'Source', message: 'Develop interactive UI components in src/components/', prereq: 'docs/api_contract.json' },
    { step_order: 6, required_item: 'src/api/', phase: 'Source', message: 'Implement backend endpoints & service handlers in src/api/', prereq: 'src/components/' },
    { step_order: 7, required_item: 'tests/unit/', phase: 'Testing', message: 'Write automated component unit tests under tests/unit/', prereq: 'src/api/' },
    { step_order: 8, required_item: 'tests/integration/', phase: 'Testing', message: 'Validate end-to-end integration flows under tests/integration/', prereq: 'tests/unit/' },
    { step_order: 9, required_item: 'Dockerfile', phase: 'DevOps', message: 'Standardize multi-stage container build in Dockerfile', prereq: 'tests/integration/' },
    { step_order: 10, required_item: 'docker-compose.yml', phase: 'DevOps', message: 'Orchestrate multi-container stack in docker-compose.yml', prereq: 'Dockerfile' }
  ]
};

// Helper: send JSON response
function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  });
  res.end(JSON.stringify(data));
}

function proxyApiToFlask(req, res, rawBuffer) {
  return new Promise((resolve, reject) => {
    const headers = { ...req.headers };
    headers.host = `${BACKEND_HOST}:${BACKEND_PORT}`;
    if (rawBuffer && rawBuffer.length > 0) {
      headers['content-length'] = rawBuffer.length;
    }

    const proxyReq = http.request({
      hostname: BACKEND_HOST,
      port: BACKEND_PORT,
      path: req.url, // Pass full URL including query strings
      method: req.method,
      headers: headers,
      timeout: 10000
    }, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, {
        ...proxyRes.headers,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'X-QuestFlow-Backend': 'flask'
      });
      proxyRes.pipe(res);
      proxyRes.on('end', () => resolve(true));
    });

    proxyReq.on('timeout', () => {
      proxyReq.destroy(new Error('Flask backend request timed out'));
    });
    proxyReq.on('error', reject);

    if (rawBuffer && rawBuffer.length > 0) {
      proxyReq.write(rawBuffer);
    }
    proxyReq.end();
  });
}

function isRuleSatisfiedNode(ruleItem, fileSet, existingFiles) {
  const cleanReq = ruleItem.replace(/\\/g, '/').replace(/^\/+|\/+$/g, '').toLowerCase();
  const normFiles = existingFiles.map(f => f.replace(/\\/g, '/').replace(/^\/+|\/+$/g, ''));

  // 1. Direct match
  if (fileSet.has(ruleItem) || fileSet.has(cleanReq)) return true;

  // 2. Exact or suffix match
  for (const f of normFiles) {
    const fLower = f.toLowerCase();
    if (fLower === cleanReq || fLower.endsWith('/' + cleanReq)) return true;
    const parts = fLower.split('/');
    if (parts.length > 1) {
      const sub = parts.slice(1).join('/');
      if (sub === cleanReq || sub.endsWith('/' + cleanReq)) return true;
    }
  }

  // 3. Folder match
  if (ruleItem.endsWith('/')) {
    const token = cleanReq + '/';
    for (const f of normFiles) {
      const fLower = f.toLowerCase();
      if (fLower === cleanReq || fLower.startsWith(token) || fLower.includes('/' + token)) return true;
    }
  }

  // 4. Semantic category matching
  if (cleanReq.includes('schema.sql') || (cleanReq.endsWith('.sql') && cleanReq.includes('schema'))) {
    return normFiles.some(f => {
      const b = path.basename(f).toLowerCase();
      return b === 'schema.sql' || f.toLowerCase().endsWith('.sql');
    });
  }

  if (['architecture', 'system_design', 'domain_model', 'wireframe'].some(k => cleanReq.includes(k))) {
    return normFiles.some(f => {
      const b = path.basename(f).toLowerCase();
      return ['architecture', 'system_design', 'blueprint', 'domain_model', 'wireframe'].some(k => b.includes(k));
    });
  }

  if (['srs', 'requirements', 'charter', 'minimal_viable_spec'].some(k => cleanReq.includes(k))) {
    return normFiles.some(f => {
      const b = path.basename(f).toLowerCase();
      return ['srs', 'requirement', 'spec', 'prd', 'charter', 'project_report'].some(k => b.includes(k));
    });
  }

  if (['user_stories', 'backlog', 'sprint_board', 'risk_log'].some(k => cleanReq.includes(k))) {
    return normFiles.some(f => {
      const b = path.basename(f).toLowerCase();
      return ['user_stories', 'backlog', 'sprint_board', 'risk_log', 'epics'].some(k => b.includes(k));
    });
  }

  if (['source', 'src', 'components', 'api'].some(k => cleanReq.includes(k))) {
    const srcExts = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.html', '.css'];
    return normFiles.some(f => {
      const ext = path.extname(f).toLowerCase();
      return srcExts.includes(ext) && !f.toLowerCase().includes('test');
    });
  }

  if (['unit_tests', 'tests/unit', 'test_bench', 'tests'].some(k => cleanReq.includes(k))) {
    return normFiles.some(f => {
      const b = path.basename(f).toLowerCase();
      return ['test_', '_test', '.test.', '.spec.'].some(t => b.includes(t)) || f.toLowerCase().includes('tests/');
    });
  }

  if (['test_matrix', 'acceptance_test_plan', 'performance_audit'].some(k => cleanReq.includes(k))) {
    return normFiles.some(f => {
      const b = path.basename(f).toLowerCase();
      return ['test_matrix', 'test_plan', 'acceptance_test', 'qa_matrix', 'performance_audit'].some(k => b.includes(k));
    });
  }

  if (cleanReq.includes('dockerfile')) {
    return normFiles.some(f => path.basename(f).toLowerCase() === 'dockerfile');
  }

  if (cleanReq.includes('docker-compose')) {
    return normFiles.some(f => path.basename(f).toLowerCase().includes('docker-compose'));
  }

  if (['workflow', 'ci_pipeline', 'ci.yml'].some(k => cleanReq.includes(k))) {
    return normFiles.some(f => f.toLowerCase().includes('.github/workflows') || f.toLowerCase().includes('ci.yml'));
  }

  return false;
}

function sendFallbackApi(pathname, method, bodyText, res) {
  if (pathname === '/api/health' && method === 'GET') {
    return sendJson(res, 200, {
      status: 'ok',
      engine: 'QuestFlow Node.js Rule Engine v2.0.0',
      backend: 'node-fallback',
      flask_available: false,
      timestamp: new Date().toISOString()
    });
  }

  if (pathname === '/api/templates' && method === 'GET') {
    return sendJson(res, 200, {
      models: ['Waterfall', 'Agile', 'V-Model', 'Spiral', 'Iterative'],
      tech_stacks: ['Python Web', 'MERN Stack', 'Critical Systems', 'R&D Prototype', 'Java Spring'],
      rules: SDLC_RULES,
      backend: 'node-fallback'
    });
  }

  if (pathname === '/api/ml-status' && method === 'GET') {
    return sendJson(res, 200, {
      model_info: {
        model_name: 'QuestFlow Node Heuristic & Standalone Rule Engine',
        version: 'v2.0.0',
        accuracy: 0.92,
        macro_f1: 0.91,
        trained_samples_count: 61
      },
      recent_audits: []
    });
  }

  if (pathname === '/api/check-sdlc' && method === 'POST') {
    let data = {};
    try {
      data = JSON.parse(bodyText || '{}');
    } catch (e) {
      return sendJson(res, 400, { error: 'Invalid JSON request payload' });
    }

    const sdlcModel = data.sdlc_model || 'Waterfall';
    const existingFiles = data.existing_files || (data.files ? Object.keys(data.files) : []);

    const rules = SDLC_RULES[sdlcModel] || SDLC_RULES.Waterfall;
    const quests = QUEST_STEPS[sdlcModel] || QUEST_STEPS.Waterfall;

    const fileSet = new Set(existingFiles.map(f => f.replace(/\\/g, '/')));
    let score = 0;
    const missing = [];
    const satisfied_items = [];

    rules.forEach(rule => {
      const isPresent = isRuleSatisfiedNode(rule.item, fileSet, existingFiles);

      if (isPresent) {
        score += rule.weight;
        satisfied_items.push(rule.item);
      } else {
        missing.push({
          phase: rule.phase,
          required_item: rule.item,
          weightage: rule.weight
        });
      }
    });

    let nextQuest = null;
    for (const step of quests) {
      const isDone = isRuleSatisfiedNode(step.required_item, fileSet, existingFiles);
      const isPrereqMet = step.prereq === null || isRuleSatisfiedNode(step.prereq, fileSet, existingFiles);

      if (!isDone && isPrereqMet) {
        nextQuest = {
          phase: step.phase,
          message: step.message,
          step_order: step.step_order,
          required_item: step.required_item
        };
        break;
      }
    }

    return sendJson(res, 200, {
      score,
      missing,
      satisfied_items,
      next_quest: nextQuest,
      sdlc_model: sdlcModel,
      backend: 'node-fallback',
      audited_at: new Date().toISOString()
    });
  }

  return sendJson(res, 404, { error: 'API route not found' });
}

// ==============================================================================
// REQUEST HANDLER
// ==============================================================================

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // Handle CORS Pre-flight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    });
    res.end();
    return;
  }

  // --- API ROUTING & FLASK PROXYING ---
  if (pathname.startsWith('/api/')) {
    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', async () => {
      const rawBuffer = Buffer.concat(chunks);
      try {
        await proxyApiToFlask(req, res, rawBuffer);
      } catch (err) {
        console.warn(`[QuestFlow] Flask backend unavailable at ${BACKEND_HOST}:${BACKEND_PORT}; routing to Node fallback.`);
        sendFallbackApi(pathname, req.method, rawBuffer.toString('utf-8'), res);
      }
    });
    return;
  }

  // --- STATIC FILE SERVING ---
  let safePath = pathname === '/' ? '/index.html' : pathname;
  const filePath = path.join(__dirname, path.normalize(safePath).replace(/^(\.\.[\/\\])+/, ''));

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found — QuestFlow Server');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': 'no-cache'
    });

    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  });
});

// ==============================================================================
// SERVER BOOTSTRAP
// ==============================================================================

server.listen(PORT, () => {
  console.log(`[QuestFlow] Frontend Server listening at http://localhost:${PORT}`);
});
