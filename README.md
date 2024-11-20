# Project convert drawio to java code 

### start

#### 1. Create a virtual environment
```bash
    python3 -m venv venv
```

#### 2. Activate de virtual envrionment
```bash
    source venv/bin/activate  #sous linux

    venv\Scripts\activate     #sous windows
```

#### 3. Install dependences
```bash
    pip install -r requirements.txt 
```


for the console execution you will create folder generated/java in the main of project
```bash
   mkdir -p generated/java
```

#### 4. Start the project
```bash
    cd src

    flask run     #for the api version

    python3 main.py    #for the cosole version
```

#### 4. Desactivate de virtual environment
```bash
    deactivate
```
