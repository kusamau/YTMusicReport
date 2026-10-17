## sonar failure

\`\`\`
12:34:46.490 INFO  Scanner configuration file: /opt/sonar-scanner-8.1.0.6389-linux-x64/conf/sonar-scanner.properties
12:34:46.495 INFO  Project root configuration file: NONE
12:34:46.510 INFO  SonarScanner CLI 8.1.0.6389
12:34:46.518 INFO  Linux 7.0.0-111034-tuxedo amd64
12:34:49.443 INFO  Communicating with SonarQube Community Build 26.8.0.126808
12:34:49.444 INFO  JRE provisioning is disabled
12:34:49.445 INFO  Using the java executable '/opt/sonar-scanner-8.1.0.6389-linux-x64/jre/bin/java' from JAVA_HOME
12:34:49.865 INFO  Starting SonarScanner Engine...
12:34:49.866 INFO  Java 21.0.9 Eclipse Adoptium (64-bit)
12:34:53.059 INFO  Load global settings
12:34:53.188 INFO  Load global settings (done) | time=127ms
12:34:53.192 INFO  Server id: 84ABEE94-AZ_vnTEOPFGwQ5z6rjk8
12:34:53.207 INFO  Loading required plugins
12:34:53.208 INFO  Load plugins index
12:34:53.226 INFO  Load plugins index (done) | time=19ms
12:34:53.227 INFO  Load/download plugins
12:34:53.258 INFO  Load/download plugins (done) | time=32ms
12:34:53.653 INFO  Process project properties
12:34:53.674 INFO  Process project properties (done) | time=21ms
12:34:53.693 INFO  Project key: YTMusicReport
12:34:53.694 INFO  Base dir: /var/jenkins_home/workspace/YTMusicReport
12:34:53.695 INFO  Working dir: /var/jenkins_home/workspace/YTMusicReport/.scannerwork
12:34:53.712 INFO  Load project settings for component key: 'YTMusicReport'
12:34:53.736 INFO  Load project settings for component key: 'YTMusicReport' (done) | time=24ms
12:34:53.780 INFO  Load quality profiles
12:34:53.845 INFO  Load quality profiles (done) | time=65ms
12:34:53.918 INFO  Load active rules
12:34:54.216 INFO  Load active rules (done) | time=297ms
12:34:54.229 INFO  Load analysis cache
12:34:54.248 INFO  Load analysis cache | time=19ms
12:34:54.397 INFO  Preprocessing files...
12:34:54.448 INFO  1 language detected in 3 preprocessed files (done) | time=51ms
12:34:54.449 INFO  0 files ignored because of scm ignore settings
12:34:54.451 INFO  Loading plugins for detected languages
12:34:54.452 INFO  Load/download plugins
12:34:54.459 INFO  Load/download plugins (done) | time=7ms
12:34:54.647 INFO  Load project repositories
12:34:54.792 INFO  Load project repositories (done) | time=144ms
12:34:54.826 INFO  Indexing files...
12:34:54.827 INFO  Project configuration:
12:34:54.841 INFO  3 files indexed (done) | time=14ms
12:34:54.843 INFO  Quality profile for py: Sonar way
12:34:54.843 INFO  ------------- Run sensors on module YTMusicReport
12:34:54.892 INFO  Load metrics repository
12:34:54.928 INFO  Load metrics repository (done) | time=36ms
12:34:55.640 INFO  Sensor IaC hadolint report Sensor [iac]
12:34:55.641 INFO  Sensor IaC hadolint report Sensor [iac] (done) | time=1ms
12:34:55.642 INFO  Sensor Java Config Sensor [iac]
12:34:55.682 INFO  There are no files to be analyzed for the Java language
12:34:55.683 INFO  Sensor Java Config Sensor [iac] (done) | time=39ms
12:34:55.683 INFO  Sensor IaC Docker Sensor [iac]
12:34:55.684 INFO  There are no files to be analyzed for the Docker language
12:34:55.684 INFO  Sensor IaC Docker Sensor [iac] (done) | time=1ms
12:34:55.685 INFO  Sensor Python Sensor [python]
12:34:55.688 WARN  Your code is analyzed as compatible with all Python 3 versions by default. You can get a more precise analysis by setting the exact Python version in your configuration via the parameter "sonar.python.version"
12:34:56.251 INFO  Starting global symbols computation
12:34:56.257 INFO  3 source files to be analyzed
12:34:56.540 INFO  3/3 source files have been analyzed
12:34:56.543 INFO  Finished step global symbols computation in 288ms
12:34:56.589 INFO  Starting rules execution
12:34:56.589 INFO  3 source files to be analyzed
12:34:57.967 INFO  3/3 source files have been analyzed
12:34:57.967 INFO  Finished step rules execution in 1377ms
12:34:57.967 INFO  The Python analyzer was able to leverage cached data from previous analyses for 0 out of 3 files. These files were not parsed.
12:34:57.971 INFO  Sensor Python Sensor [python] (done) | time=2288ms
12:34:57.972 INFO  Sensor Cobertura Sensor for Python coverage [python]
12:34:57.991 INFO  Sensor Cobertura Sensor for Python coverage [python] (done) | time=19ms
12:34:57.991 INFO  Sensor PythonXUnitSensor [python]
12:34:57.997 INFO  Sensor PythonXUnitSensor [python] (done) | time=6ms
12:34:57.998 INFO  Sensor Import of Bandit issues [python]
12:34:57.999 INFO  Importing /var/jenkins_home/workspace/YTMusicReport/security-reports/bandit.json
12:34:58.006 INFO  Sensor Import of Bandit issues [python] (done) | time=8ms
12:34:58.006 INFO  Sensor Python Dependency Sensor [python]
12:34:58.010 INFO  Sensor Python Dependency Sensor [python] (done) | time=4ms
12:34:58.010 INFO  Sensor TextAndSecretsSensor [text]
12:34:58.028 INFO  Available processors: 16
12:34:58.028 INFO  Using 16 threads for analysis.
12:34:58.351 INFO  The property "sonar.tests" is not set. To improve the analysis accuracy, we categorize a file as a test file if any of the following is true:
  * The filename starts with "test"
  * The filename contains "test." or "tests."
  * Any directory in the file path is named: "doc", "docs", "test", "tests", "mock" or "mocks"
  * Any directory in the file path has a name ending in "test" or "tests"

12:34:58.390 INFO  Start fetching files for the text and secrets analysis
12:34:58.402 INFO  Using Git CLI to retrieve dirty files
12:34:58.412 INFO  Retrieving language associated files and files included via "sonar.text.inclusions" that are tracked by git
12:34:58.412 INFO  Starting the text and secrets analysis
12:34:58.414 INFO  3 source files to be analyzed for the text and secrets analysis
12:34:58.431 INFO  3/3 source files have been analyzed for the text and secrets analysis
12:34:58.434 INFO  Sensor TextAndSecretsSensor [text] (done) | time=423ms
12:34:58.439 INFO  ------------- Run sensors on project
12:34:58.683 INFO  Sensor Import external issues report from SARIF file.
12:34:58.683 WARN  Property 'sonar.sarifReportPaths' is not declared as multi-values/property set but was read using 'getStringArray' method. The SonarQube plugin declaring this property should be updated.
12:34:59.016 INFO  File security-reports/opengrep.sarif: 1 run(s) successfully imported (0 vulnerabilities in total).
12:34:59.017 INFO  File security-reports/osv.sarif: 0 run(s) successfully imported (0 vulnerabilities in total).
12:34:59.017 INFO  Sensor Import external issues report from SARIF file. (done) | time=333ms
12:34:59.018 INFO  Sensor IaC Project Sensor [iac]
12:34:59.018 INFO  Sensor IaC Project Sensor [iac] (done) | time=1ms
12:34:59.019 INFO  Sensor Zero Coverage Sensor
12:34:59.041 INFO  Sensor Zero Coverage Sensor (done) | time=22ms
12:34:59.042 INFO  ------------- Gather SCA dependencies on project
12:34:59.046 INFO  Dependency analysis skipped
12:34:59.057 INFO  CPD Executor 1 file had no CPD blocks
12:34:59.058 INFO  CPD Executor Calculating CPD for 2 files
12:34:59.069 INFO  CPD Executor CPD calculation finished (done) | time=11ms
12:34:59.078 INFO  SCM revision ID 'c62ddb4ebacc2d93d471d20dd37fe417859c386c'
12:34:59.168 INFO  Analysis report generated in 89ms, dir size=350.6 kB
12:34:59.189 INFO  Analysis report compressed in 20ms, zip size=69.1 kB
12:34:59.231 INFO  Analysis report uploaded in 41ms
12:34:59.232 INFO  ANALYSIS SUCCESSFUL, you can find the results at: http://sonarqube:9000/dashboard?id=YTMusicReport
12:34:59.232 INFO  Note that you will be able to access the updated dashboard once the server has processed the submitted analysis report
12:34:59.232 INFO  More about the report processing at http://sonarqube:9000/api/ce/task?id=cff3356e-20b7-4da4-8c2b-df3bc42fbe98
12:34:59.240 INFO  Analysis total time: 5.927 s
12:34:59.242 INFO  SonarScanner Engine completed successfully
12:34:59.367 INFO  EXECUTION SUCCESS
12:34:59.368 INFO  Total time: 12.921s
\`\`\`
