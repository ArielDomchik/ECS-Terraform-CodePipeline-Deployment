pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
		dir('/home/ubuntu/workspace/ecs-project/src'){
		sh 'nohup python3 server.py'
            }
      }
}
	stage('Test') {
	    steps {
		dir('/home/ubuntu/workspace/Weather Application Pipeline/web/webproject') {
		sh 'python3 seleniumunit.py'
		}
	}
}
	stage('Push') {
	    steps {
                sh 'aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 646360616404.dkr.ecr.us-east-1.amazonaws.com'
                docker build -t app-repo . 
                docker tag app-repo:latest 646360616404.dkr.ecr.us-east-1.amazonaws.com/app-repo:latest
                docker push 646360616404.dkr.ecr.us-east-1.amazonaws.com/app-repo:latest
		}
}
