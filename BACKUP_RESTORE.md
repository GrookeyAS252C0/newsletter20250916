# バックアップと復元手順

## 📦 バックアップ情報

**バックアップ作成日**: 2025年10月25日
**バージョン**: v1.0-stable-20251025
**コミットID**: 77d4aac

### 安定版の特徴

✅ **季節を考慮した天気コメント生成**
- 日付から季節を自動判定
- 季節+天気+気圧+月齢を総合的に判断
- 受験生向け200文字健康アドバイス生成

✅ **月齢計算の精度向上**
- 基準新月を更新（2000年→2024年）
- しきい値を厳密化（±1.0日→±0.7日）
- 外部APIとの誤差0.3日以内

✅ **月相方向の正確な認識**
- 月相情報を明示的に表示
- LLMプロンプトを強化
- 誤認識をほぼ完全に防止

### 修正済みバグ

- ❌→✅ 気温11度・雨天で「蒸し暑い」と表示される問題
- ❌→✅ 月齢計算のズレ（2日のズレを修正）
- ❌→✅ 月相方向の誤認識（「新月に向かう」と誤表示）

---

## 🔄 復元方法

### 方法1: タグから復元（推奨）

現在の変更を破棄して、安定版に戻す場合：

```bash
# 現在の変更をすべて破棄
git reset --hard HEAD

# 安定版タグをチェックアウト
git checkout v1.0-stable-20251025

# masterブランチに戻って安定版を適用
git checkout master
git reset --hard v1.0-stable-20251025
git push origin master --force
```

### 方法2: バックアップブランチから復元

```bash
# バックアップブランチをチェックアウト
git checkout backup/stable-20251025

# masterブランチに戻って復元
git checkout master
git reset --hard backup/stable-20251025
git push origin master --force
```

### 方法3: 特定のファイルのみ復元

特定のファイルだけ安定版に戻す場合：

```bash
# 例: health_knowledge_rag.py だけ復元
git checkout v1.0-stable-20251025 -- health_knowledge_rag.py

# 複数ファイルを復元
git checkout v1.0-stable-20251025 -- health_knowledge_rag.py weather_service.py
```

---

## 📋 確認コマンド

### バックアップの存在確認

```bash
# タグ一覧を表示
git tag -l

# バックアップブランチを表示
git branch -a | grep backup

# 特定のタグの情報を表示
git show v1.0-stable-20251025
```

### 現在の状態確認

```bash
# 現在のコミットを確認
git log --oneline -1

# 安定版との差分を確認
git diff v1.0-stable-20251025
```

---

## ⚠️ 注意事項

1. **強制プッシュ（--force）は慎重に**
   - 他の人と共同作業している場合は事前に連絡
   - 念のため現在の状態もバックアップ推奨

2. **復元前に必ず確認**
   ```bash
   # 現在の変更を確認
   git status
   git diff
   ```

3. **復元後の動作確認**
   ```bash
   # 依存関係の再インストール
   pip install -r requirements.txt

   # アプリケーションのテスト実行
   streamlit run streamlit_app.py
   ```

---

## 📞 トラブルシューティング

### Q: 復元したが動作しない

```bash
# Python環境をクリーン
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Q: タグが見つからない

```bash
# リモートからタグを取得
git fetch --tags
git tag -l
```

### Q: 復元を取り消したい

```bash
# 直前の状態に戻る（復元の復元）
git reflog
git reset --hard HEAD@{1}
```

---

## 🔖 追加のバックアップ作成

将来、新しい安定版を作成する場合：

```bash
# 新しいタグを作成（日付を更新）
git tag -a v1.1-stable-YYYYMMDD -m "説明"

# 新しいバックアップブランチを作成
git branch backup/stable-YYYYMMDD

# リモートにプッシュ
git push origin v1.1-stable-YYYYMMDD
git push origin backup/stable-YYYYMMDD
```

---

## 📚 関連リンク

- GitHubリポジトリ: https://github.com/GrookeyAS252C0/newsletter20250916
- 安定版タグ: https://github.com/GrookeyAS252C0/newsletter20250916/releases/tag/v1.0-stable-20251025
- バックアップブランチ: https://github.com/GrookeyAS252C0/newsletter20250916/tree/backup/stable-20251025
