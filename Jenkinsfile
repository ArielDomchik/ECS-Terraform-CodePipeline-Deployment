pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                dir('/home/ubuntu/workspace/ecs-project/src') {
                    sh 'docker build -t app-repo .'
                    sh 'docker run -d -p 5000:5000 app-repo --name app-repo'
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
        stage('Clean') {
          steps {
              dir('/home/ubuntu/workspace/ecs-project/src') {
                  sh 'docker stop app-repo'
                  sh 'docker rm app-repo'
               }
            }
        }
        stage('Push') {
            steps {
                dir('/home/ubuntu/workspace/ecs-project/src') {
                    sh 'aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 646360616404.dkr.ecr.us-east-1.amazonaws.com'
                    sh 'docker tag app-repo:latest 646360616404.dkr.ecr.us-east-1.amazonaws.com/app-repo:latest'
                    sh 'docker push 646360616404.dkr.ecr.us-east-1.amazonaws.com/app-repo:latest'
                }
            }
        }
    }
}
