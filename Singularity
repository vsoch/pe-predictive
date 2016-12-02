Bootstrap: docker
From: vanessa/pefinder

%runscript

    cd /code/pefinder
    exec /opt/conda/bin/python /code/pefinder/cli.py "$@"


%post

    chmod -R 777 /data
    /opt/conda/bin/python -m nltk.downloader -d /usr/local/share/nltk_data all
    echo "To run, ./pefinder.img --help"
