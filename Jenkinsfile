pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                dir('/home/ubuntu/workspace/ecs-project/src') {
                    sh 'pip install requirements.txt'
                    sh 'nohup python3 server.py'
                }
            }
        }
        stage('Test') {
            steps {
                dir('/home/ubuntu/workspace/ecs-project/src') {
                    sh 'python3 seleniumunit.py'
                }
            }
        }
        stage('Push') {
            steps {
                dir('/home/ubuntu/workspace/ecs-project/src') {
                    sh 'aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 646360616404.dkr.ecr.us-east-1.amazonaws.com'
                    sh 'docker build -t app-repo .'
                    sh 'docker tag app-repo:latest 646360616404.dkr.ecr.us-east-1.amazonaws.com/app-repo:latest'
                    sh 'docker push 646360616404.dkr.ecr.us-east-1.amazonaws.com/app-repo:latest'
                }
            }
        }
    }
}
