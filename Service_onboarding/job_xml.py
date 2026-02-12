def jenkins_job_content(): 
  jenkins_job = '''<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1505.vea_4b_20a_4a_495">
  <actions>
    <org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobAction plugin="pipeline-model-definition@2.2247.va_423189a_7dff"/>
    <org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobPropertyTrackerAction plugin="pipeline-model-definition@2.2247.va_423189a_7dff">
      <jobProperties>
        <string>org.jenkinsci.plugins.workflow.job.properties.DisableConcurrentBuildsJobProperty</string>
      </jobProperties>
      <triggers/>
      <parameters/>
      <options/>
    </org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobPropertyTrackerAction>
  </actions>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>15</daysToKeep>
        <numToKeep>15</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
        <removeLastBuild>false</removeLastBuild>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
    <org.jenkinsci.plugins.workflow.job.properties.DisableConcurrentBuildsJobProperty>
      <abortPrevious>false</abortPrevious>
    </org.jenkinsci.plugins.workflow.job.properties.DisableConcurrentBuildsJobProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.ChoiceParameterDefinition>
          <name>VERSION</name>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>Patch</string>
              <string>Minor</string>
              <string>Major</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>ENVIRONMENT</name>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>dev</string>
              <string>venus</string>
              <string>prod</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>BRANCH</name>
          <defaultValue>develop</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>UNIVERSITY</name>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>common</string>
              <string>atlas</string>
              <string>andhra</string>
              <string>bharathidasan</string>
              <string>centurion</string>
              <string>chandigarh</string>
              <string>drmgr</string>
              <string>dypatil</string>
              <string>jain</string>
              <string>jnu</string>
              <string>kiit</string>
              <string>kuk</string>
              <string>niu</string>
              <string>vgu</string>
              <string>vistas</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@4046.v90b_1b_9edec67">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@5.7.0">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>git@bitbucket.org:upgrad_dev/pedagogy.git</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/${{BRANCH}}</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>'''
  return jenkins_job