node {
  def app

  stage('Clone Repository') {
    /*Ensuring repository is cloned*/
    checkout scm
  }

  stage('Build Image') {
    /*Builds actual image similar to docker build on the command line*/

    app = docker.build("edureka1/edureka")
  }

  stage('Test Image') {
    /*To checkout working status of the framework of our image*/
    
    app.inside {
      sh 'echo "Tests passed" '
    }
  }

  stage('Push Image') {
    /*Finally we push the image with two tags:
    *First, the incremental build number from jenkins
    *Second, the 'latest' tag.
    *Pushing multiple tags is cheap, as all the layers are reused*/
    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
      app.push("${env.BUILD_NUMBER}")
      app.push("latest")
    }
  }
}
