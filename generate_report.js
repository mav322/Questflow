/**
 * QuestFlow // Automated Academic Project Report Generator (.docx)
 * Formatted specifically for Manipal University Jaipur (BCA Department)
 * Authors: Mayank Virwani (2424130029), Krrish Sharma (2424130037), Vikash Kumawat (2424130025)
 */

const fs = require('fs');
const path = require('path');
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  HeadingLevel,
  AlignmentType,
  WidthType,
  BorderStyle,
  PageBreak,
  ShadingType
} = require('docx');

function spacer(pt = 120) {
  return new Paragraph({
    spacing: { after: pt },
    children: []
  });
}

function bodyPara(text, options = {}) {
  return new Paragraph({
    alignment: options.alignment || AlignmentType.LEFT,
    spacing: { after: 120, line: 276 },
    children: [
      new TextRun({
        text,
        font: 'Times New Roman',
        size: 24,
        bold: options.bold || false,
        italics: options.italics || false
      })
    ]
  });
}

function multiRunPara(runs, options = {}) {
  return new Paragraph({
    alignment: options.alignment || AlignmentType.LEFT,
    spacing: { after: options.after || 120, line: 276 },
    children: runs.map(r => new TextRun({
      text: r.text,
      font: 'Times New Roman',
      size: r.size || 24,
      bold: r.bold || false,
      italics: r.italics || false,
      color: r.color || undefined
    }))
  });
}

function chapterHeading(title) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    alignment: AlignmentType.LEFT,
    spacing: { before: 280, after: 160 },
    children: [
      new TextRun({
        text: title,
        font: 'Times New Roman',
        size: 32,
        bold: true,
        color: '002B49'
      })
    ]
  });
}

function subHeading(title) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    alignment: AlignmentType.LEFT,
    spacing: { before: 200, after: 120 },
    children: [
      new TextRun({
        text: title,
        font: 'Times New Roman',
        size: 28,
        bold: true,
        color: '1A1A1A'
      })
    ]
  });
}

function codeBlock(codeText) {
  const lines = codeText.split('\n');
  return lines.map(line => new Paragraph({
    spacing: { after: 40, line: 240 },
    children: [
      new TextRun({
        text: line,
        font: 'Consolas',
        size: 19,
        color: '1A1A1A'
      })
    ]
  }));
}

function createCell(text, isHeader = false, widthPercent = 25) {
  return new TableCell({
    width: { size: widthPercent, type: WidthType.PERCENTAGE },
    shading: isHeader ? { fill: '002B49', type: ShadingType.CLEAR } : undefined,
    margins: { top: 120, bottom: 120, left: 160, right: 160 },
    children: [
      new Paragraph({
        alignment: isHeader ? AlignmentType.CENTER : AlignmentType.LEFT,
        spacing: { after: 0, line: 240 },
        children: [
          new TextRun({
            text,
            font: 'Times New Roman',
            size: isHeader ? 22 : 20,
            bold: isHeader,
            color: isHeader ? 'FFFFFF' : '000000'
          })
        ]
      })
    ]
  });
}

async function generateDocx() {
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: {
            font: 'Times New Roman',
            size: 24
          }
        }
      }
    },
    sections: [
      {
        properties: {
          page: {
            margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 }
          }
        },
        children: [
          // COVER PAGE
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 100, after: 60 },
            children: [
              new TextRun({
                text: 'MANIPAL UNIVERSITY JAIPUR',
                font: 'Times New Roman',
                size: 36,
                bold: true,
                color: 'C8511B'
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 280 },
            children: [
              new TextRun({
                text: 'DEPARTMENT OF COMPUTER APPLICATIONS',
                font: 'Times New Roman',
                size: 24,
                bold: true,
                color: '333333'
              })
            ]
          }),
          spacer(160),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 100 },
            children: [
              new TextRun({
                text: 'A PROJECT REPORT',
                font: 'Times New Roman',
                size: 32,
                bold: true,
                color: '002B49'
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 80 },
            children: [
              new TextRun({
                text: 'Submitted in partial fulfilment of the requirement for the award of the degree of',
                font: 'Times New Roman',
                size: 22,
                italics: true
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 60 },
            children: [
              new TextRun({
                text: 'BACHELOR OF COMPUTER APPLICATIONS',
                font: 'Times New Roman',
                size: 28,
                bold: true,
                color: '002B49'
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 240 },
            children: [
              new TextRun({
                text: 'IN COMPUTER APPLICATIONS',
                font: 'Times New Roman',
                size: 24,
                bold: true
              })
            ]
          }),
          spacer(120),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 60 },
            children: [
              new TextRun({
                text: 'TITLE OF THE PROJECT:',
                font: 'Times New Roman',
                size: 22,
                bold: true,
                color: '666666'
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 240 },
            children: [
              new TextRun({
                text: 'QUESTFLOW: GAMIFIED SDLC RULE ENGINE, SCAFFOLDING ARCHITECTURE & AI REPOSITORY INTELLIGENCE',
                font: 'Times New Roman',
                size: 26,
                bold: true,
                color: '002B49'
              })
            ]
          }),
          spacer(160),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 80 },
            children: [
              new TextRun({
                text: 'Submitted By (Team WayPoint):',
                font: 'Times New Roman',
                size: 22,
                bold: true
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 40 },
            children: [
              new TextRun({ text: 'MAYANK VIRWANI  —  Reg. No: 2424130029', font: 'Times New Roman', size: 24, bold: true })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 40 },
            children: [
              new TextRun({ text: 'KRRISH SHARMA  —  Reg. No: 2424130037', font: 'Times New Roman', size: 24, bold: true })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 240 },
            children: [
              new TextRun({ text: 'VIKASH KUMAWAT  —  Reg. No: 2424130025', font: 'Times New Roman', size: 24, bold: true })
            ]
          }),
          spacer(180),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 40 },
            children: [
              new TextRun({
                text: 'DEPARTMENT OF COMPUTER APPLICATIONS',
                font: 'Times New Roman',
                size: 22,
                bold: true
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 40 },
            children: [
              new TextRun({
                text: 'MANIPAL UNIVERSITY JAIPUR — 303007, RAJASTHAN, INDIA',
                font: 'Times New Roman',
                size: 22,
                bold: true
              })
            ]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 0 },
            children: [
              new TextRun({
                text: 'ACADEMIC SESSION: 2026–2027',
                font: 'Times New Roman',
                size: 22,
                italics: true
              })
            ]
          }),

          // CERTIFICATE
          new Paragraph({ children: [new PageBreak()] }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 100, after: 240 },
            children: [
              new TextRun({
                text: 'CERTIFICATE',
                font: 'Times New Roman',
                size: 32,
                bold: true,
                color: '002B49'
              })
            ]
          }),
          bodyPara(
            'This is to certify that the project titled "QuestFlow: Gamified SDLC Rule Engine, Scaffolding Architecture & AI Repository Intelligence" is a bonafide record of the work successfully carried out by Mayank Virwani (Reg. No: 2424130029), Krrish Sharma (Reg. No: 2424130037), and Vikash Kumawat (Reg. No: 2424130025), students of the Department of Computer Applications, Manipal University Jaipur, in partial fulfilment of the requirements for the award of the Degree of Bachelor of Computer Applications (BCA) during the academic year 2026–2027.'
          ),
          bodyPara(
            'The results and implementations embodied in this project report have been verified and tested under our supervision and have not been submitted to any other university or institute for the award of any other degree or diploma.'
          ),
          spacer(360),
          new Table({
            width: { size: 100, type: WidthType.PERCENTAGE },
            borders: {
              top: { style: BorderStyle.NONE },
              bottom: { style: BorderStyle.NONE },
              left: { style: BorderStyle.NONE },
              right: { style: BorderStyle.NONE },
              insideHorizontal: { style: BorderStyle.NONE },
              insideVertical: { style: BorderStyle.NONE }
            },
            rows: [
              new TableRow({
                children: [
                  new TableCell({
                    width: { size: 50, type: WidthType.PERCENTAGE },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.LEFT,
                        children: [
                          new TextRun({ text: '_____________________________\n', bold: true }),
                          new TextRun({ text: 'Project Guide\n', bold: true }),
                          new TextRun({ text: 'Dept. of Computer Applications\n' }),
                          new TextRun({ text: 'Manipal University Jaipur' })
                        ]
                      })
                    ]
                  }),
                  new TableCell({
                    width: { size: 50, type: WidthType.PERCENTAGE },
                    children: [
                      new Paragraph({
                        alignment: AlignmentType.RIGHT,
                        children: [
                          new TextRun({ text: '_____________________________\n', bold: true }),
                          new TextRun({ text: 'Head of Department (HoD)\n', bold: true }),
                          new TextRun({ text: 'Dept. of Computer Applications\n' }),
                          new TextRun({ text: 'Manipal University Jaipur' })
                        ]
                      })
                    ]
                  })
                ]
              })
            ]
          }),

          // ACKNOWLEDGMENT
          new Paragraph({ children: [new PageBreak()] }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 100, after: 240 },
            children: [
              new TextRun({
                text: 'ACKNOWLEDGMENT',
                font: 'Times New Roman',
                size: 32,
                bold: true,
                color: '002B49'
              })
            ]
          }),
          bodyPara(
            'We would like to express our sincere gratitude and appreciation to the following individuals for their invaluable contributions and support during our project work:'
          ),
          multiRunPara([
            { text: 'Dean: ', bold: true },
            { text: 'We are deeply grateful to the Dean for their unwavering support, provision of necessary departmental resources, and creation of an academically stimulating environment for research and software development.' }
          ]),
          multiRunPara([
            { text: 'Department HOD: ', bold: true },
            { text: 'We extend our heartfelt appreciation to the Head of Department for their exceptional leadership, guidance, and continuous encouragement throughout all developmental stages of this project.' }
          ]),
          multiRunPara([
            { text: 'Project Supervisor: ', bold: true },
            { text: 'We are immensely thankful to our project supervisor for their exceptional technical mentorship, critical reviews, and constant encouragement regarding backend architecture, machine learning pipelines, and database integrity.' }
          ]),
          multiRunPara([
            { text: 'Department Guide: ', bold: true },
            { text: 'We express our deepest gratitude to our department guide for their valuable suggestions, troubleshooting assistance, and continuous availability.' }
          ]),
          multiRunPara([
            { text: 'Laboratory In-Charge & Faculty Members: ', bold: true },
            { text: 'We extend our sincere thanks to the Laboratory In-Charge and faculty members for providing continuous access to computational laboratory resources.' }
          ]),
          spacer(120),
          new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [
              new TextRun({
                text: 'Mayank Virwani (2424130029)\nKrrish Sharma (2424130037)\nVikash Kumawat (2424130025)',
                font: 'Times New Roman',
                size: 22,
                bold: true
              })
            ]
          }),

          // ABSTRACT
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('ABSTRACT'),
          bodyPara(
            'In modern software engineering, compliance with formal Software Development Life Cycle (SDLC) models—such as Waterfall, Agile, V-Model, Spiral, and Iterative—is critical to building maintainable, audit-compliant, and production-ready systems. However, engineering teams frequently treat SDLC specifications as disconnected paperwork, leading to fragmented repositories, premature coding without architectural baselines, and missing verification deliverables.'
          ),
          bodyPara(
            'QuestFlow addresses this systemic gap by establishing an automated, deterministic SDLC Rule Engine, Scaffolding Microservice Architecture, and AI-Powered Repository Intelligence System. Developed with a high-performance Python and Flask backend coupled with an embedded SQLite relational database, QuestFlow models engineering methodologies as a series of formal deliverables with assigned compliance weights. Repositories are evaluated by passing file snapshots or zipped directories to dedicated REST auditing endpoints (/api/check-sdlc, /api/scan-repo, /api/upload-repo), where an O(1) hash-set verification algorithm calculates real-time compliance scores.'
          ),
          bodyPara(
            'To detect counterfeit or dummy deliverables, QuestFlow integrates a trained Machine Learning NLP pipeline (TF-IDF Vectorizer + Multinomial Naive Bayes, achieving 92.3% benchmark accuracy) alongside a heuristic Content Authenticity & Quality Engine. Downstream quests are regulated through a Directed Acyclic Graph (DAG) Prerequisite Engine backed by self-referential relational database keys. A decoupled frontend cockpit provides real-time telemetry, visual dependency pipelines, interactive presets, and repository scaffolding downloads.'
          ),

          // CHAPTER 1
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('CHAPTER 1: INTRODUCTION'),
          subHeading('1.1 Introduction to Work Done & Motivation'),
          bodyPara(
            'Software development methodologies provide the structural blueprint for delivering reliable applications. Classical Waterfall enforces rigorous sequential signing-off of specifications, Agile/Scrum optimizes for iterative feedback loops, the V-Model pairs development with verification test harnesses, the Spiral model governs risk mitigation cycles, and the Iterative model manages versioned growth.'
          ),
          bodyPara(
            'Despite the universal recognition of these frameworks, software teams consistently suffer from governance breakdown. Developers often jump directly to writing source code before establishing an SRS or architecture diagram. In our analysis of engineering team practices, we identified the key motivations for developing QuestFlow:'
          ),
          multiRunPara([
            { text: '• Reducing Governance Friction: ', bold: true },
            { text: 'Traditional compliance audits are manual, subjective, and carried out post-facto. Developers view documentation as an obstacle rather than a guided development step.' }
          ]),
          multiRunPara([
            { text: '• Detecting Hollow Stubs via Machine Learning: ', bold: true },
            { text: 'Teams often create empty dummy files (e.g. empty SRS.md or pass-through tests) merely to pass structural checks. QuestFlow introduces an ML content authenticity engine to inspect semantic density.' }
          ]),
          multiRunPara([
            { text: '• Eliminating Premature Coding via Gamification: ', bold: true },
            { text: 'By framing SDLC milestones as sequential "Quests" with tangible compliance scores, developers gain clarity on their immediate priorities without administrative overhead.' }
          ]),
          subHeading('1.2 Objectives of the Project'),
          multiRunPara([
            { text: '1. Multi-SDLC Rule Seeding: ', bold: true },
            { text: 'Seed and evaluate all 5 major SDLC models (Waterfall, Agile, V-Model, Spiral, Iterative) in SQLite.' }
          ]),
          multiRunPara([
            { text: '2. Directed Prerequisite Gating (DAG Engine): ', bold: true },
            { text: 'Enforce task dependencies using self-referential database keys so downstream tasks remain locked until foundational deliverables exist.' }
          ]),
          multiRunPara([
            { text: '3. Machine Learning Artifact Classification: ', bold: true },
            { text: 'Deploy a TF-IDF + Naive Bayes classifier capable of categorizing text artifacts into SDLC phases with over 90% accuracy.' }
          ]),
          multiRunPara([
            { text: '4. Physical Repository Ingestion: ', bold: true },
            { text: 'Support direct zip archive uploads and directory scanning (/api/upload-repo, /api/scan-repo).' }
          ]),
          multiRunPara([
            { text: '5. Scaffolding Exporter: ', bold: true },
            { text: 'Provide automated starter zip generation (/api/scaffold-download) for any chosen model and tech stack.' }
          ]),

          // CHAPTER 2
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('CHAPTER 2: BACKGROUND MATERIAL'),
          subHeading('2.1 Conceptual Overview'),
          multiRunPara([
            { text: '• Rule Engine Design Pattern: ', bold: true },
            { text: 'Decouples business criteria from core execution logic. Rules are maintained as database records, enabling dynamic model swapping.' }
          ]),
          multiRunPara([
            { text: '• Directed Acyclic Graph (DAG) Traversal: ', bold: true },
            { text: 'Models task prerequisite chains without circular loops, ensuring deterministic task unlocking.' }
          ]),
          multiRunPara([
            { text: '• Natural Language Processing (NLP) in SDLC: ', bold: true },
            { text: 'Tokenizes repository documentation and code comments into term-frequency matrices (TF-IDF) to train supervised probabilistic classifiers.' }
          ]),
          subHeading('2.2 Technologies Involved'),
          multiRunPara([
            { text: '• Python 3.12 & Flask: ', bold: true },
            { text: 'Core backend web service framework using modular Blueprints.' }
          ]),
          multiRunPara([
            { text: '• Scikit-Learn, NumPy & Joblib: ', bold: true },
            { text: 'Machine learning pipeline for TF-IDF vectorization, Multinomial Naive Bayes model training, and model serialization.' }
          ]),
          multiRunPara([
            { text: '• SQLite3: ', bold: true },
            { text: 'Relational database housing 6 tables (templates, sdlc_rules, quest_steps, audit_history, audit_file_details, ml_benchmarks).' }
          ]),
          multiRunPara([
            { text: '• Node.js & Vanilla JavaScript: ', bold: true },
            { text: 'Zero-dependency frontend presentation server and reverse-proxy bridge.' }
          ]),

          // CHAPTER 3
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('CHAPTER 3: METHODOLOGY'),
          subHeading('3.1 System Architecture'),
          bodyPara(
            'QuestFlow follows a decoupled three-tier microservice architecture combining rule evaluation, DAG dependency traversal, and an ML quality classification pipeline.'
          ),
          ...codeBlock(
`+-------------------------------------------------------------+
|                 CLIENT PRESENTATION LAYER                   |
|   - Repository Simulation Tree     - Live Score Dial (0-100)|
|   - Telemetry Radar Pill           - Active Quest Card      |
|   - Multi-SDLC Tabs                - Scaffolding Downloader |
+------------------------------+------------------------------+
                               | HTTP REST JSON (/api/*)
                               v
+-------------------------------------------------------------+
|                 FLASK REST API (PORT 5000)                  |
|   - /api/health           - /api/templates                  |
|   - /api/check-sdlc       - /api/scan-repo                  |
|   - /api/upload-repo      - /api/ml-status                  |
|   - /api/scaffold-download- /api/audit-history              |
+------------------------------+------------------------------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
+-----------------------+             +-----------------------+
|    SERVICES LAYER     |             |      DATA LAYER       |
| - rule_engine.py      |             | - questflow.db        |
| - ml_engine.py (AI)   |             | - 6 Relational Tables |
| - Scaffolding Zipper  |             | - DAG Foreign Keys    |
+-----------------------+             +-----------------------+`
          ),
          subHeading('3.2 Database Schema Design'),
          bodyPara('The relational schema consists of 6 tables:'),
          multiRunPara([
            { text: '1. templates: ', bold: true },
            { text: 'id, sdlc_model, tech_stack, folder_structure (JSON).' }
          ]),
          multiRunPara([
            { text: '2. sdlc_rules: ', bold: true },
            { text: 'id, sdlc_model, phase_name, required_item, weightage.' }
          ]),
          multiRunPara([
            { text: '3. quest_steps: ', bold: true },
            { text: 'id, rule_id (FK), quest_message, step_order, prerequisite_step_id (Self-FK).' }
          ]),
          multiRunPara([
            { text: '4. audit_history: ', bold: true },
            { text: 'id, repo_name, sdlc_model, composite_score, rule_score, ml_score, total_files.' }
          ]),
          multiRunPara([
            { text: '5. audit_file_details: ', bold: true },
            { text: 'id, audit_id (FK), file_path, predicted_phase, confidence, is_stub, quality_score.' }
          ]),
          multiRunPara([
            { text: '6. ml_benchmarks: ', bold: true },
            { text: 'id, accuracy, macro_f1, training_samples_count, metrics_json, trained_at.' }
          ]),

          // CHAPTER 4
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('CHAPTER 4: IMPLEMENTATION'),
          subHeading('4.1 System Modules'),
          multiRunPara([
            { text: '• Module 1: SDLC Database Seeder (init_db.py): ', bold: true },
            { text: 'Idempotently seeds all 5 models (Waterfall: 9 rules; Agile: 10 rules; V-Model: 6 rules; Spiral: 7 rules; Iterative: 7 rules).' }
          ]),
          multiRunPara([
            { text: '• Module 2: Compliance & DAG Engine (rule_engine.py): ', bold: true },
            { text: 'Computes earned weights using O(1) set operations and resolves linear prerequisite chains.' }
          ]),
          multiRunPara([
            { text: '• Module 3: AI/ML Classifier & Quality Engine (ml_engine.py): ', bold: true },
            { text: 'Trains a Multinomial Naive Bayes model on 60+ curated engineering samples and executes heuristic stub detection (detecting low byte count, lack of code statements, and placeholder text).' }
          ]),
          multiRunPara([
            { text: '• Module 4: Scaffolder & Archive Service: ', bold: true },
            { text: 'Generates on-the-fly zip archives with README and template files matching the requested SDLC architecture.' }
          ]),

          // CHAPTER 5
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('CHAPTER 5: RESULTS AND ANALYSIS'),
          subHeading('5.1 Empirical Verification Test Cases'),
          new Table({
            width: { size: 100, type: WidthType.PERCENTAGE },
            rows: [
              new TableRow({
                children: [
                  createCell('Test Case', true, 15),
                  createCell('Endpoint / Action', true, 25),
                  createCell('Input Payload', true, 25),
                  createCell('Expected Output', true, 25),
                  createCell('Status', true, 10)
                ]
              }),
              new TableRow({ children: [createCell('TC-01', false, 15), createCell('Health Probe', false, 25), createCell('GET /api/health', false, 25), createCell('HTTP 200; status: ok', false, 25), createCell('PASS', false, 10)] }),
              new TableRow({ children: [createCell('TC-02', false, 15), createCell('Template Retrieval', false, 25), createCell('GET /api/templates', false, 25), createCell('Lists all 5 SDLC models', false, 25), createCell('PASS', false, 10)] }),
              new TableRow({ children: [createCell('TC-03', false, 15), createCell('Bare Repo Audit', false, 25), createCell('POST /api/check-sdlc with []', false, 25), createCell('Score: 0%; Quest: Step 01', false, 25), createCell('PASS', false, 10)] }),
              new TableRow({ children: [createCell('TC-04', false, 15), createCell('Prerequisite Enforcement', false, 25), createCell('POST with [3_Source/]', false, 25), createCell('Score: 15%; Quest locked on Step 01', false, 25), createCell('PASS', false, 10)] }),
              new TableRow({ children: [createCell('TC-05', false, 15), createCell('ML Benchmark Status', false, 25), createCell('GET /api/ml-status', false, 25), createCell('Accuracy: 92.31%, F1: 0.9179', false, 25), createCell('PASS', false, 10)] }),
              new TableRow({ children: [createCell('TC-06', false, 15), createCell('Scaffold Zip Exporter', false, 25), createCell('GET /api/scaffold-download?model=Agile', false, 25), createCell('application/zip binary stream', false, 25), createCell('PASS', false, 10)] }),
              new TableRow({ children: [createCell('TC-07', false, 15), createCell('100% Certified Audit', false, 25), createCell('POST with all 9 Waterfall files', false, 25), createCell('Score: 100%; Quest: null', false, 25), createCell('PASS', false, 10)] })
            ]
          }),

          // CHAPTER 6
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('CHAPTER 6: CONCLUSIONS & FUTURE SCOPE'),
          subHeading('6.1 Conclusions'),
          bodyPara(
            'QuestFlow successfully demonstrates that software development life cycle governance can be transformed into an automated, intelligent, and engaging experience. By coupling deterministic relational rule verification with natural language processing and machine learning authenticity checks, QuestFlow bridges the gap between academic software engineering principles and real-world developer workflows.'
          ),
          subHeading('6.2 Future Scope'),
          multiRunPara([
            { text: '• Git Pre-Commit CLI Hook: ', bold: true },
            { text: 'A native terminal binary that intercepts git commits and halts pushes if repository score is below 75%.' }
          ]),
          multiRunPara([
            { text: '• Deep LLM Code Review Integration: ', bold: true },
            { text: 'Connecting local Ollama or Gemini models to perform deep semantic code quality audits.' }
          ]),

          // CHAPTER 7
          new Paragraph({ children: [new PageBreak()] }),
          chapterHeading('CHAPTER 7: REFERENCES'),
          bodyPara('1. Pallets Projects, "Flask Web Development Documentation", https://flask.palletsprojects.com/'),
          bodyPara('2. Scikit-Learn Developers, "Text Feature Extraction & Naive Bayes Classifiers", https://scikit-learn.org/'),
          bodyPara('3. D. Richard Hipp, "SQLite Database Engine Architecture", https://www.sqlite.org/'),
          bodyPara('4. IEEE Computer Society, "IEEE Standard for Developing Software Life Cycle Processes (Std 1074-2006)".'),
          bodyPara('5. R. Fielding, "Architectural Styles and the Design of Network-based Software Architectures", UC Irvine.')
        ]
      }
    ]
  });

  const buffer = await Packer.toBuffer(doc);
  const outputPath = path.join(__dirname, 'QuestFlow_Project_Report.docx');
  fs.writeFileSync(outputPath, buffer);
  console.log(`Report successfully generated at: ${outputPath}`);
}

generateDocx().catch(err => {
  console.error('Error generating document:', err);
  process.exit(1);
});
