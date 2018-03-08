FROM python:2-onbuild

USER root


COPY myapp.py /src/myapp.py
COPY newpolicy.json /src/newpolicy.json
CMD ["python","/src/myapp.py"]
