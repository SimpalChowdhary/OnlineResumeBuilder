pipeline {
    agent any

    environment {
        KUBECONFIG = 'C:\\Users\\ASUS\\.kube\\config'
        LOCAL_IMAGE = 'onlineresumebuilder:v1'
        DOCKER_IMAGE = 'simpalchowdhary/onlineresumebuilder:v1'
    }

    stages {
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t onlineresumebuilder:v1 .'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_TOKEN'
                )]) {
                    bat 'echo %DOCKER_TOKEN% | docker login -u %DOCKER_USER% --password-stdin'
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                bat 'docker tag %LOCAL_IMAGE% %DOCKER_IMAGE%'
                bat 'docker push %DOCKER_IMAGE%'
            }
        }

        stage('Check Kubernetes Access') {
            steps {
                bat 'where kubectl'
                bat 'kubectl config current-context'
                bat 'kubectl cluster-info'
                bat 'kubectl get nodes'
            }
        }
        

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl apply -f deployment.yaml'
                bat 'kubectl apply -f service.yaml'
            }
        }

        stage('Verify Deployment') {
            steps {
                bat 'kubectl rollout status deployment/onlineresumebuilder-deployment --timeout=180s'
                bat 'kubectl get pods'
                bat 'kubectl get services'
            }
        }
    }

    post {
        success {
            echo 'Online Resume Builder deployed successfully!'
            echo 'Application URL: http://localhost:30089'
        }

        failure {
            echo 'Pipeline failed. Check the Console Output for the error.'
        }

        always {
            bat 'docker logout || exit /b 0'
        }
    }
}
