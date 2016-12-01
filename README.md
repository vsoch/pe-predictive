# pefinder Docker

This is a Docker image that will run PE-Finder to produce output for some input data file. 

Packages that need to be installed (e.g. seaborn and radnlp) have versions specified in case a future change breaks this code, you can see this in the top section of the [Dockerfile](Dockerfile).


## Getting Started
You should first [install Docker](https://docs.docker.com/engine/installation/) and then build the container:

    docker build -t vanessa/pefinder .

You also need to install something called [Docker Compose](https://docs.docker.com/compose/install/), which is a nice way of putting containers together. Once you have done this, there is a simple command for starting the entire application.

    docker-compose up

"Up" means "bring it up." If we add the "-d" option this would detach it.

If you need to restart or stop you can just press Control+C. If you use the detached option, then you would do:

      docker-compose restart pefinder
      docker-compose stop pedinfer

If you want to see running images:

      docker ps


## How do I shell into the container?
First you need to know the container id. If you do `docker ps` you will see it running as *_notebook_1. There is a weird 12 character code by its name, this is it's container-id `af21bf1d48a6` 

>> pro-tip: this is actually the first 12 characters of the image md5-sum! It's a much longer string, but we only need 12 to distinguish containers on a user local machine

Once we have the id, we can shell into it with the following command:

      docker exec -it af21bf1d48a6 bash

This says we want to execute (exec) and (interactive)(terminal) for container with id (af21bf1d48a6) and run the command (bash)


# Why?
By "shipping" analyses in packages, meaning having a specification of all dependencies (python modules, data, etc.) we can be assured that the next person that runs our analysis will not run into system-specific differences. They won't have to install python or anaconda to run our notebook, and get a weird message about having the wrong kernel. They just need Docker, and then to run the image, and that's it. This is an important feature of reproducible workflows and analyses, and every piece of code that you work on (and tend to share) should have features like this.
