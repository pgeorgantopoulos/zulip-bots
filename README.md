# zulip-bots

## Installation
Clone the repo and install requirements.
```bash
git clone https://github.com/pgeorgantopoulos/zulip-bots.git zulip-bots
cd zulip-bots/
pip install -r requirements.txt
```
## Copy credentials to .zuliprc
Copy credentials from zulip app to `novel-objects-arXiv/.zuliprc` and `physicscv-arXiv/.zuliprc`.

## Verify scripts running properly
```bash
python bot.py --config_path novel-objects-arXiv
python bot.py --config_path physicscv-arXiv
```

Onwards set desired python in `run_all_bots.sh` with

```bash
sed -i "s|<path/to/python>|$(which python)|g" run_all_bots.sh
```

## Verify shell script runs properly for all bots

```bash
bash run_all_bots.sh
```

## Schedule your bot with crontab run

Run the following command to get input for crontab
```bash
echo "0 10 * * 1 bash $(pwd)/run_all_bots.sh "
```

Take the output and append it to
```bash
crontab -e
```
