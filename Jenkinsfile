pipeline {
    agent any

    environment {
        IMAGE_NAME = "emailapp:latest"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Pulling project source code..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    bat "docker build -t %IMAGE_NAME% ."
                }
            }
        }

        stage('Run Docker Container') {
            environment {
                EMAIL_ADDRESS = credentials('gmail_email')
                APP_PASSWORD = credentials('gmail_app_password')
            }
            steps {
                script {
                    echo "Running container with secure environment variables..."
                    bat """
                        docker run -d --name emailapp_local -p 5000:5000 ^
                        -e EMAIL_ADDRESS=%EMAIL_ADDRESS% ^
                        -e APP_PASSWORD=%APP_PASSWORD% ^
                        %IMAGE_NAME%
                    """
                }
            }
        }

        stage('Test App') {
            steps {
                echo "Checking if container is running..."
                bat 'docker ps'
            }
        }
    }

    post {
        always {
            echo "Cleaning up old containers..."
            bat 'docker stop emailapp_local || exit 0'
            bat 'docker rm emailapp_local || exit 0'
        }
    }
}

