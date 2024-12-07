# VS Slumbot

## 概要
このプロジェクトは、ポーカーAIの「Slumbot」に対して勝ち越せるアルゴリズムの開発を目的としています。ヘッズアップノーリミットテキサスホールデムにおいて、Slumbotに対して正の期待値を出せる戦略の実装と検証を行います。

## プロジェクトの目標
Slumbotに対して安定して勝ち越せるポーカーアルゴリズムの開発と実装

## 前提条件
プロジェクトを始める前に、以下の要件を満たしていることを確認してください：
- Python 3.8以上
- pip（Pythonパッケージインストーラー）
- Git（バージョン管理用）

## インストール方法

1. リポジトリのクローン:
```bash
git clone https://github.com/yourusername/vs_slumbot.git
cd vs_slumbot
```

2. 仮想環境の作成と有効化（推奨）:
```bash
python -m venv venv
# Windowsの場合:
venv\Scripts\activate
# Unix または MacOSの場合:
source venv/bin/activate
```

3. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本的な使用方法
Slumbotとの対戦を開始：
```bash
python src/main.py --hands <ハンド数>
```

### 認証情報を使用する場合
Slumbotのアカウント情報がある場合：
```bash
python src/main.py --hands <ハンド数> --username <ユーザー名> --password <パスワード>
```

### 出力について
実行ごとに`logs`フォルダ内に新しいセッションディレクトリが作成され、以下のファイルが生成されます：
- セッションログ（`session.log`）：詳細なハンド情報
- グラフ（`session_graph.png`）：収支の推移

---

# English

## Overview
This project aims to develop a poker algorithm that can consistently win against Slumbot, a poker AI. The goal is to implement and test various strategies to achieve a positive win rate in heads-up no-limit Texas hold'em poker.

## Project Goal
To develop and implement a poker algorithm capable of beating Slumbot consistently.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vs_slumbot.git
cd vs_slumbot
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
To play hands against Slumbot:
```bash
python src/main.py --hands <number_of_hands>
```

### With Authentication
If you have Slumbot credentials:
```bash
python src/main.py --hands <number_of_hands> --username <your_username> --password <your_password>
```

### Output
The script will create a new session directory in the `logs` folder for each run, containing:
- A log file (`session.log`) with detailed hand information
- A graph (`session_graph.png`) showing the cumulative winnings/losses

## Project Structure
```
vs_slumbot/
├── LICENSE
├── README.md
├── requirements.txt
├── sample/
│   └── slumbot_api.py
├── src/
│   ├── api/
│   ├── analysis/
│   └── utils/
└── logs/
```

## License
This project is licensed under [LICENSE] - see the LICENSE file for details.