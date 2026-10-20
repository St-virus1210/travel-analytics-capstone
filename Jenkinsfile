pipeline {
  agent any
  environment {
    IMAGE_NAME = 'travel-analytics-api'
    IMAGE_TAG = "${env.BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Install') {
      steps {
        sh 'python -m pip install --upgrade pip'
        sh 'pip install -r requirements.txt'
      }
    }
    stage('Tests') {
      steps { sh 'PYTHONPATH=src pytest -q' }
    }
    stage('Train and evaluate') {
      steps { sh 'PYTHONPATH=src python -m travel_analytics.train --data-dir data --artifact-dir artifacts' }
    }
    stage('Build image') {
      steps { sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .' }
    }
    // Configure registry credentials and deployment stages explicitly for your environment.
    stage('Push image (optional)') {
      when { expression { return env.DOCKER_REGISTRY?.trim() } }
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-registry', usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_PASSWORD')]) {
          sh 'echo "$REGISTRY_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$REGISTRY_USER" --password-stdin'
          sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} $DOCKER_REGISTRY/${IMAGE_NAME}:${IMAGE_TAG}'
          sh 'docker push $DOCKER_REGISTRY/${IMAGE_NAME}:${IMAGE_TAG}'
        }
      }
    }
  }
  post { always { junit allowEmptyResults: true, testResults: 'test-results/*.xml' } }
}
