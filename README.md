# gha-sl-ot-DFqwfc8werfy
1. turn on venv

```
python3 -m venv venv
source venv/bin/activate
```
2. install requirements

```
pip install -r requirements.txt
```
3. Turn on app

```
export GITHUB_TOKEN=$GH-TOKEN"
python app.py
```
4. Test

```
curl "http://localhost:5000/deployments?env=qa"
```
5. Deactivate env

```
deactivate
```