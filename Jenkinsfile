// ============================================================================
// local-ci universal Jenkinsfile — copy this into your project's repository root.
//
// It configures ITSELF. The first stage inspects the checkout (pom.xml,
// package.json, pyproject.toml, ...) and every later stage gates on what it
// found, so a project with no Maven module never runs a Maven build and a
// project with no package.json never runs npm audit. Copy it unchanged and it
// should do the right thing; the environment { } block below is the one place
// you ever need to edit.
//
// Generate a pre-filled copy instead of editing by hand:
//     cd /path/to/your-project
//     /path/to/local-ci/server/generate-jenkinsfile.sh
// Add --prune to physically delete the stages your project doesn't need (see
// templates/README.md for the trade-off).
//
// A stage skipped by when { } still APPEARS in the Jenkins stage view, greyed
// out as "skipped" — Declarative Pipeline offers no way to hide it. That is
// deliberate here: the pipeline documents what it is not doing, and every copy
// of this file stays diffable against the upstream one as steps are added. Use
// generate-jenkinsfile.sh --prune if you would rather not see them at all.
//
// Fails fast by default: if Java build & test doesn't pass, every later stage
// (Java dependency CVEs, Frontend, SonarQube) is skipped rather than run
// against code that doesn't even pass its own tests — dependencyCheckGate()
// alone can cost 10-40 minutes on a cold NVD cache, which is wasted time once
// the build itself is red. Set CI_FAIL_FAST = 'false' below to go back to
// running every stage regardless, if you'd rather have every report in one
// pass than the fastest possible signal.
// ============================================================================
@Library('local-ci') _

pipeline {
    agent any

    // ------------------------------------------------------------------
    // THE ONE EDIT POINT.
    //
    // Every CI_* toggle below is 'auto' by default, meaning "decide from what is
    // actually in the checkout". Set one to 'true' or 'false' to override the
    // detection for this project. The free-form values are 'auto' too — set them
    // when the detected guess is wrong.
    //
    // These live in environment { } rather than a `def` above pipeline { } on
    // purpose: a script-level local is invisible to methods and to some
    // directives declared in the same Jenkinsfile.
    // ------------------------------------------------------------------
    environment {
        CI_MAVEN    = 'false'  // Java build + test    (mavenBuild)
        CI_DEPCHECK = 'false'  // Java dependency CVEs (dependencyCheckGate)
        CI_NODE     = 'false'  // npm audit            (npmAuditGate)
        CI_SONAR    = 'true'   // SonarQube analysis   (sonarScan)
        CI_OPENGREP = 'true'   // SAST + intra-file taint analysis (opengrepScan)
        CI_BANDIT   = 'true'   // Python SAST          (banditScan)
        CI_GITLEAKS = 'true'   // Git history secrets  (gitleaksScan)
        CI_OSV      = 'true'   // dependency CVEs      (osvScan)

        CI_MAVEN_POM         = 'auto'   // e.g. 'backend/pom.xml'
        CI_MAVEN_GOALS       = 'clean verify'
        CI_NODE_DIR          = 'auto'   // e.g. 'app/web'
        CI_SONAR_PROJECT_KEY = 'YTMusicReport'  // e.g. 'my-app'
        CI_SONAR_SOURCES     = 'src'    // e.g. 'app/backend/src/main/java,app/web/src'
        // A project-local OpenGrep config file or directory may replace this
        // image-baked immutable community ruleset.
        CI_OPENGREP_RULES     = 'auto'
        // Comma-separated Python roots for Bandit. 'auto' accepts only the
        // conventional src/app/lib/source directories detector verified contain
        // Python files; override for a non-conventional layout.
        CI_BANDIT_PATHS       = 'src'

        // Dependency-Check is report-only until a project has triaged its
        // backlog: findings colour the build UNSTABLE without breaking it. Set a
        // number (7.0 = High and Critical) to turn it into a real gate.
        CI_DEPCHECK_FAIL_ON_CVSS = ''

        // Stop the whole pipeline the moment Java build & test fails, skipping
        // every stage after it (dependencyCheckGate, npm audit, sonarScan)
        // rather than spending minutes analyzing code that doesn't even pass
        // its own tests. 'false' restores the old behavior: every stage runs
        // regardless, so a single push surfaces every unrelated finding at
        // once. This is the one CI_* toggle that changes CONTROL FLOW rather
        // than which stages exist - see the "Java build & test" stage below.
        CI_FAIL_FAST = 'true'
    }

    options {
        // Only core directives here: the local-ci Jenkins image installs a
        // deliberately short plugin list, so options like timestamps() (the
        // Timestamper plugin) would fail the pipeline before it starts.
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    stages {
        // >>> local-ci:stage:detect
        stage('Detect project stack') {
            steps {
                script {
                    def stack = detectProjectStack()

                    // 'auto' resolves to what was detected; anything else wins.
                    // Assigned to env here rather than declared in environment { }
                    // above because a pipeline-level environment { } block cannot
                    // read a value computed in an earlier stage.
                    def resolve = { String override, String detected ->
                        override == null || override == 'auto' || override == '' ? detected : override
                    }

                    env.LCI_RUN_MAVEN    = resolve(env.CI_MAVEN,    stack.HAS_MAVEN)
                    env.LCI_RUN_DEPCHECK = resolve(env.CI_DEPCHECK, stack.HAS_MAVEN)
                    env.LCI_RUN_NODE     = resolve(env.CI_NODE,     stack.HAS_NODE)
                    // Sonar is worth running for any language it can see; gate it
                    // on having found *some* source directory to point it at.
                    env.LCI_RUN_SONAR    = resolve(env.CI_SONAR,    stack.SONAR_SOURCES ? 'true' : 'false')
                    env.LCI_RUN_OPENGREP = resolve(env.CI_OPENGREP, stack.SONAR_SOURCES ? 'true' : 'false')
                    def inferredPythonRoots = stack.SONAR_SOURCES.tokenize(',').findAll { root ->
                        root == 'src' || root == 'app' || root == 'lib' || root == 'source' ||
                            root.endsWith('/src') || root.endsWith('/app') ||
                            root.endsWith('/lib') || root.endsWith('/source')
                    }
                    env.LCI_BANDIT_PATHS  = resolve(env.CI_BANDIT_PATHS, inferredPythonRoots.join(','))
                    env.LCI_RUN_BANDIT    = resolve(env.CI_BANDIT,
                        stack.HAS_PYTHON == 'true' && env.LCI_BANDIT_PATHS ? 'true' : 'false')
                    env.LCI_RUN_GITLEAKS = resolve(env.CI_GITLEAKS, 'true')
                    def hasOsvInput = stack.HAS_MAVEN == 'true' || stack.HAS_NODE == 'true' || stack.HAS_PYTHON == 'true'
                    env.LCI_RUN_OSV      = resolve(env.CI_OSV,      hasOsvInput ? 'true' : 'false')

                    env.LCI_MAVEN_POM         = resolve(env.CI_MAVEN_POM,         stack.MAVEN_POM ?: 'pom.xml')
                    // A multi-module reactor wants one aggregated report at the
                    // root rather than one per module.
                    env.LCI_DEPCHECK_GOAL     = stack.MAVEN_MULTIMODULE == 'true' ? 'aggregate' : 'check'
                    env.LCI_NODE_DIR          = resolve(env.CI_NODE_DIR,          (stack.NODE_DIRS ?: '.').tokenize(',')[0])
                    env.LCI_SONAR_KEY         = resolve(env.CI_SONAR_PROJECT_KEY, stack.PROJECT_NAME)
                    env.LCI_SONAR_SOURCES     = resolve(env.CI_SONAR_SOURCES,     stack.SONAR_SOURCES)
                    env.LCI_OPENGREP_RULES    = resolve(env.CI_OPENGREP_RULES, '/opt/opengrep-rules/configs/security-audit.list')
                    env.LCI_LANGS             = stack.LANGS

                    echo """Resolved pipeline configuration:
  Maven build          : ${env.LCI_RUN_MAVEN}    (pom: ${env.LCI_MAVEN_POM})
  Dependency-Check     : ${env.LCI_RUN_DEPCHECK} (goal: ${env.LCI_DEPCHECK_GOAL})
  npm audit            : ${env.LCI_RUN_NODE}     (dir: ${env.LCI_NODE_DIR})
  OpenGrep SAST         : ${env.LCI_RUN_OPENGREP} (rules: ${env.LCI_OPENGREP_RULES})
  Bandit Python SAST    : ${env.LCI_RUN_BANDIT} (paths: ${env.LCI_BANDIT_PATHS ?: '(none)'})
  Gitleaks history      : ${env.LCI_RUN_GITLEAKS}
  OSV dependency CVEs   : ${env.LCI_RUN_OSV}
  SonarQube            : ${env.LCI_RUN_SONAR}    (key: ${env.LCI_SONAR_KEY}, sources: ${env.LCI_SONAR_SOURCES})
  Languages detected   : ${env.LCI_LANGS ?: '(none)'}
  Fail fast on build   : ${env.CI_FAIL_FAST} (skips later stages if Java build & test fails)"""
                }
            }
        }
        // <<< local-ci:stage:detect

        // >>> local-ci:stage:maven
        stage('Java build & test') {
            when { expression { env.LCI_RUN_MAVEN == 'true' } }
            steps {
                script {
                    if (env.CI_FAIL_FAST == 'true') {
                        // Deliberately NOT wrapped in catchError: an uncaught
                        // failure here makes Declarative Pipeline skip every
                        // remaining stage and go straight to post { } below -
                        // no time spent on dependencyCheckGate() (10-40 min on
                        // a cold NVD cache) or sonarScan() against code that
                        // doesn't even pass its own tests. post { failure { ... } }
                        // right below, and the pipeline-level report delivery,
                        // both still fire normally: an uncaught stage exception
                        // sets the stage (and build) result to FAILURE exactly
                        // like catchError does - it just also stops execution
                        // instead of continuing past it. mavenBuild() itself
                        // already tees its log and publishes JUnit results
                        // before rethrowing, so the archiveFailure() call below
                        // still has a real log to archive.
                        mavenBuild(
                            pom: env.LCI_MAVEN_POM,
                            goals: env.CI_MAVEN_GOALS,
                            logFile: 'maven-build.log',
                        )
                    } else {
                        catchError(stageResult: 'FAILURE') {
                            mavenBuild(
                                pom: env.LCI_MAVEN_POM,
                                goals: env.CI_MAVEN_GOALS,
                                logFile: 'maven-build.log',
                            )
                        }
                    }
                }
            }
            post {
                failure { script { archiveFailure('maven-build', 'maven-build.log') } }
            }
        }
        // <<< local-ci:stage:maven

        // >>> local-ci:stage:depcheck
        stage('Java dependency CVEs') {
            when { expression { env.LCI_RUN_DEPCHECK == 'true' } }
            steps {
                // buildResult: 'UNSTABLE' rather than 'FAILURE' while
                // CI_DEPCHECK_FAIL_ON_CVSS is empty: findings colour the build
                // without breaking it. See templates/README.md's "ratchet" note.
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    script {
                        def threshold = env.CI_DEPCHECK_FAIL_ON_CVSS?.trim()
                        dependencyCheckGate(
                            pom: env.LCI_MAVEN_POM,
                            goal: env.LCI_DEPCHECK_GOAL,
                            failOnCvss: threshold ? threshold.toDouble() : null,
                            logFile: 'dependency-check.log',
                        )
                    }
                }
            }
            post {
                unstable { script { archiveFailure('dependency-check', 'dependency-check.log') } }
                failure  { script { archiveFailure('dependency-check', 'dependency-check.log') } }
            }
        }
        // <<< local-ci:stage:depcheck

        // >>> local-ci:stage:node
        stage('Frontend (npm audit)') {
            when { expression { env.LCI_RUN_NODE == 'true' } }
            steps {
                catchError(stageResult: 'FAILURE') {
                    dir(env.LCI_NODE_DIR) {
                        sh 'npm ci'
                        npmAuditGate('npm-audit.log')
                    }
                }
            }
            post {
                failure { script { archiveFailure('npm-audit', "${env.LCI_NODE_DIR}/npm-audit.log") } }
                always {
                    // Best-effort: files a GitHub issue per new high/critical
                    // npm-audit finding, deduped across re-scans via a hidden
                    // marker. Self-gates on GIT_BRANCH (main/master only).
                    // Skipped if the 'github-issues-token' credential isn't set.
                    script {
                        try {
                            withCredentials([string(credentialsId: 'github-issues-token', variable: 'GH_TOKEN')]) {
                                dir(env.LCI_NODE_DIR) { fileNpmAuditIssuesAsGithubTasks() }
                            }
                        } catch (err) { echo "Skipping npm-audit issue filing: ${err.message}" }
                    }
                }
            }
        }
        // <<< local-ci:stage:node

        // >>> local-ci:stage:opengrep
        stage('SAST (OpenGrep)') {
            when { expression { env.LCI_RUN_OPENGREP == 'true' } }
            steps {
                // Findings leave the stage green while teams triage their
                // baseline. The wrapper exits non-zero only for scanner/report
                // errors, which then fail the build normally.
                opengrepScan(
                    paths: env.LCI_SONAR_SOURCES.tokenize(','),
                    rules: env.LCI_OPENGREP_RULES,
                    logFile: 'opengrep.log',
                )
            }
            post { failure { script { archiveFailure('opengrep', 'opengrep.log') } } }
        }
        // <<< local-ci:stage:opengrep

        // >>> local-ci:stage:bandit
        stage('SAST (Bandit)') {
            when { expression { env.LCI_RUN_BANDIT == 'true' } }
            steps {
                script {
                    if (!env.LCI_BANDIT_PATHS) {
                        error 'Python was detected but no Bandit source roots were configured; set CI_BANDIT_PATHS or disable CI_BANDIT.'
                    }
                    banditScan(paths: env.LCI_BANDIT_PATHS.tokenize(','), logFile: 'bandit.log')
                }
            }
            post { failure { script { archiveFailure('bandit', 'bandit.log') } } }
        }
        // <<< local-ci:stage:bandit

        // >>> local-ci:stage:gitleaks
        stage('Secrets (Gitleaks)') {
            when { expression { env.LCI_RUN_GITLEAKS == 'true' } }
            steps {
                gitleaksScan(logFile: 'gitleaks.log')
            }
            post { failure { script { archiveFailure('gitleaks', 'gitleaks.log') } } }
        }
        // <<< local-ci:stage:gitleaks

        // >>> local-ci:stage:osv
        stage('Dependency CVEs (OSV)') {
            when { expression { env.LCI_RUN_OSV == 'true' } }
            steps {
                osvScan(logFile: 'osv.log')
            }
            post { failure { script { archiveFailure('osv', 'osv.log') } } }
        }
        // <<< local-ci:stage:osv

        // >>> local-ci:stage:sonar
        stage('SonarQube') {
            when { expression { env.LCI_RUN_SONAR == 'true' } }
            steps {
                script {
                    catchError(stageResult: 'FAILURE') {
                    // sonar.sources points at real source dirs, never '.': a repo
                    // root almost always holds node_modules/.venv/build output,
                    // and the scanner's indexing walk can crash on those before
                    // sonar.exclusions is ever consulted.
                    def sonarArgs = [
                        "-Dsonar.projectKey=${env.LCI_SONAR_KEY}",
                        "-Dsonar.sources=${env.LCI_SONAR_SOURCES}",
                    ]
                    def sarifReports = []
                    if (env.LCI_RUN_OPENGREP == 'true') { sarifReports << 'security-reports/opengrep.sarif' }
                    if (env.LCI_RUN_OSV == 'true') { sarifReports << 'security-reports/osv.sarif' }
                    if (sarifReports) { sonarArgs << "-Dsonar.sarifReportPaths=${sarifReports.join(',')}" }
                    if (env.LCI_RUN_BANDIT == 'true') { sonarArgs << '-Dsonar.python.bandit.reportPaths=security-reports/bandit.json' }
                        sonarScan(
                            scannerArgs: sonarArgs.join(' '),
                            logFile: 'sonar.log',
                        )
                    }
                }
            }
            post {
                failure { script { archiveFailure('sonar', 'sonar.log') } }
                always {
                    script {
                        try {
                            withCredentials([string(credentialsId: 'github-issues-token', variable: 'GH_TOKEN')]) {
                                fileSonarIssuesAsGithubTasks(projectKey: env.LCI_SONAR_KEY)
                            }
                        } catch (err) { echo "Skipping SonarQube issue filing: ${err.message}" }
                    }
                }
            }
        }
        // <<< local-ci:stage:sonar

        // ------------------------------------------------------------------
        // OWASP ZAP remains a future per-project DAST integration because it
        // needs a deployed, reachable application target.
        // >>> local-ci:stage:zap
        // stage('DAST (OWASP ZAP)') {
        //     steps { zapBaselineScan(targetUrl: 'http://localhost:8080') }
        // }
        // <<< local-ci:stage:zap
        //
        // ------------------------------------------------------------------
    }

    post {
        always { archiveArtifacts artifacts: 'ci-reports/*.md,security-reports/**/*', allowEmptyArchive: true }

        // Wired from BOTH unstable and failure. Dependency-Check is report-only
        // and marks the build UNSTABLE, which does NOT trigger post { failure }
        // — so a failure-only wiring would write ci-reports/*.md and then never
        // deliver them to the PR comment or the ci-reports/<branch> ref.
        unstable { script { deliverCiReports() } }
        failure  { script { deliverCiReports() } }
    }
}

// Both delivery paths are independent and both are best-effort: set up one, the
// other, both, or neither. Declared at the top level of the file (outside
// pipeline { }) so post { unstable } and post { failure } can share it without
// duplicating eight lines.
void deliverCiReports() {
    try {
        withCredentials([string(credentialsId: 'github-pr-comment-token', variable: 'GH_TOKEN')]) {
            postPrFailureReport()
        }
    } catch (err) { echo "Skipping PR failure comment: ${err.message}" }

    try {
        withCredentials([string(credentialsId: 'github-push-token', variable: 'GH_PUSH_TOKEN')]) {
            pushCiReports()
        }
    } catch (err) { echo "Skipping ci-reports branch push: ${err.message}" }
}
