# exkanjiviz
quick-and-dirty visualizer for font data from:
- PC-6007SR Kakuchou Kanji ROM&RAM cartridge / 拡張漢字ＲＯＭ＆ＲＡＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-6601-01 Kakuchou Kanji ROM cartridge / 拡張漢字ＲＯＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-8801 series level 1 Kanji ROM `kanji1.rom`
# ... and exkanji2kanjirom
quick-and-dirty PC-6001mkII and PC-6601 Kanji ROM construction using font data from:
- PC-6007SR Kakuchou Kanji ROM&RAM cartridge / 拡張漢字ＲＯＭ＆ＲＡＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-6601-01 Kakuchou Kanji ROM cartridge / 拡張漢字ＲＯＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-8801 series level 1 Kanji ROM `kanji1.rom`

Using this script you can make a working PC-6001mkII / PC-6601 Kanji ROM from your Kakuchou Kanji ROM or PC-8801 Level 1 Kanji ROM. The PC-6001mkII and PC-6601 Kanji ROM contains a 1/4 or so subset of the Level 1 Kanji from PC-6007SR/PC-6601-01/PC-8801.

The result has exactly the same contents as the PC-6001mkII `KANJIROM.62` or PC-6601 `KANJIROM.66`.

## Usage
1. prepare your ROM image (either a real one, or a synthesized one) in `saverkanji` EXKANJI.ROM format
2. run `python exkanjiviz.py EXKANJI.ROM exkanji.png`
3. the created `exkanji.png` will have a visualization of the ROM contents laid out according to JIS ordering, which is not quite the same as the storage order
4. run `python exkanji2kanjirom.py EXKANJI.ROM kanjirom.62` (or ...`.66`)
5. the created `kanjirom.62` (or ...`.66`) should work with PC-6001mkII and PC-6601 emulators
## Visualization
Visualization of the contents of my PC-6007SR Kakuchou Kanji ROM & RAM Cartridge
<img width="4352" height="816" alt="Visualization -  N60  PC-6007SR Kakuchou Kanji ROM   RAM Cartridge (NEC) (Japan) (PC-6001mkII)" src="https://github.com/user-attachments/assets/6f0b8159-5c19-490d-9a6f-b3857a521a26" />
## ROM Data Extraction
If you need to get the data from your actual PC-6007SR cartridge or synthesize it from other font data, see the [おまけ：拡張漢字ROM
 section of the PC-6001mkII/6601用互換BASIC website](http://000.la.coocan.jp/p6/basic66.html#:~:text=%E5%A4%89%E6%8F%9B%E3%81%97%E3%81%9F%E4%BE%8B-,%E3%81%8A%E3%81%BE%E3%81%91%EF%BC%9A%E6%8B%A1%E5%BC%B5%E6%BC%A2%E5%AD%97ROM,-%E3%82%A8%E3%83%9F%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%BF%E3%81%A7%E3%81%AE). That page also links to a utility program that can convert both directions between `ksaver` EXTKANJI.ROM format and `saverkanji` EXKANJI.ROM format. I saved mine from the cartridge using a PC-6001mkII with [ksaver](https://web.archive.org/web/20071223192215/http://www.kisweb.ne.jp/personal/windy/pc6001/p6soft.html#ksaver) in EXTKANJI.ROM format and then converted it to EXKANJI.ROM format using the converter `cnvextkanji`.

The `kanji1.rom` from the PC-8801 series has identical contents to PC-6007SR's Kanji ROM in saverkanji EXKANJI.ROM format.

ROM fingerprint information for the version dumped from my cartridge:

- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [ksaver EXTKANJI format].rom crc32:7e53b7d8 md5:1268ac01f5b3c38ef2be22576e54a6b6 sha1:827aadd671347a05281a3863e20dd9f31bff5423 sha256:85f212271e79c5a727e81ec61a8cba6fdeff0123e07a1bfcec71b769d8d532dc size:131072`
- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [saverkanji EXKANJI format].rom crc32:6178bd43 md5:d81c6d5d7ad1a4bbbd6ae22a01257603 sha1:82e11a177af6a5091dd67f50a2f4bafda84d6556 sha256:7608040cffb1951e5cc567abb63f75b5746777a1ba96196c1b75606b793bb4bb size:131072`

ROM fingerprint information for the KANJIROM.62 / KANJIROM.66 created from this:
- `32K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [KANJIROM subset].rom crc32:20c8f3eb md5:638ea8e59a73fa4d8c6a6153b500dab9 sha1:4c9f30f0a2ebbe70aa8e697f94eac74d8241cadd sha256:0f536e7c00ac9985cb39dfd3c54d20bbf1c477a3fcc00f1dfad207f3323b3373 size:32768`

The 128 KiB Kakuchou Kanji ROM is actually stored in two separate 64KiB ROM IC's, with the left 8 pixels of each character in the first IC and the right 8 pixels in the second one, except for the half-width characters which are laid out differently. The on-board 32 KiB PC-6001mkII/PC-6601 Kanji ROM is apparently also stored in two separate 16 KiB ROM IC's, split in exactly the same way (except it doesn't have any halfwidth characters; for built-in text rendering those come from a separate onboard pair of 8KiB CGROM's which use a different layout - and may actually be concatenated and stored in a single 16KiB ROM IC.) So the EXTKANJI.ROM format accurately reflects a concatenation of the two individual ROM IC's, which are separately referred to as EXTKANJI1.ROM and EXTKANJI2.ROM. And EXKANJI.ROM/kanji1.rom instead interleaves them, which matches how they are used for font rendering as a virtual 64Ki x 16bit ROM - though in fact each 8 bit chunk is read out separately due to how the I/O port mapping works. The KANJIROM.62/.66 format is likewise a concatenation of the two parts, KANJIROM1.62/.66 and KANJIROM2.62/.66, each of which represents the contents of a physical ROM IC. There is not a corresponding interleaved 16Ki x 16bit format used by emulators AFAIK.

ROM fingerprint information for each of the separated parts:
- `16K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [KANJIROM subset] [IC 1].rom crc32:a5c44f92 md5:1336e0c67fb47a795fc17594685aa66a sha1:1e4a354eb647e0a8f8a2dff2088fadfe113782d6 sha256:e2b2c8eced4c373c0d06578512484af7f7a1532f043aa47f1fb8802bdf75cc25 size:16384`
- `16K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [KANJIROM subset] [IC 2].rom crc32:cc055765 md5:d86d0f5569583946ca5f2ea1e0b751a7 sha1:ddbaf2538f5e123bfa96fda35623427fd6418c75 sha256:5ef4c158915201678aca1c70a8f95b9a65b4284c1c1f5abecc0b6cbd674f917c size:16384`
- `64K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [ksaver EXTKANJI format] [IC 1].rom crc32:85540f76 md5:b467872d5d5eb00fb45d7a420980fd42 sha1:4bef3de4771aae2654af00cb96cf3254a3822e44 sha256:dceb13fe4ef764c93dbc04db71cf8f4ce67ef14c09331fcca291be4c0361649f size:65536`
- `64K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [ksaver EXTKANJI format] [IC 2].rom crc32:1764a663 md5:3bd8bf8a43aaf6d44aae5f7dfe77036f sha1:54d082778f64bf4a929e98a3cc310f51e15a8767 sha256:6d91378addf91d9d6e4b520913548a7a80822fb74bc29ae866b3af97337a0bc1 size:65536`
## Photos
<img width="40%" alt="Front - [N60] 128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan)" src="https://github.com/user-attachments/assets/410fa46d-4063-4328-91a1-74a89bf85569" /><img width="40%" alt="Back - [N60] 128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan)" src="https://github.com/user-attachments/assets/29aa6621-edea-44e7-a241-475a20d6fa3f" />
<img width="30%" alt="Interior View 1 -  N60  PC-6007SR Kakuchou Kanji ROM   RAM Cartridge (NEC) (Japan) (PC-6001mkII)" src="https://github.com/user-attachments/assets/5820b11b-4dc7-483e-80bc-61b550034469" /><img width="30%" alt="Interior View 2 -  N60  PC-6007SR Kakuchou Kanji ROM   RAM Cartridge (NEC) (Japan) (PC-6001mkII)" src="https://github.com/user-attachments/assets/e227bb76-232d-4a1b-ac05-1425b3f3782b" /><img width="30%" alt="Interior View 3 -  N60  PC-6007SR Kakuchou Kanji ROM   RAM Cartridge (NEC) (Japan) (PC-6001mkII)" src="https://github.com/user-attachments/assets/1a8392a2-d499-4341-8038-c2ec94f45d4e" />
<img width="30%" alt="Interior View 4 -  N60  PC-6007SR Kakuchou Kanji ROM   RAM Cartridge (NEC) (Japan) (PC-6001mkII)" src="https://github.com/user-attachments/assets/a323a9a1-c315-483b-9ea9-a0c2395354c7" /><img width="30%" alt="Interior View 5 -  N60  PC-6007SR Kakuchou Kanji ROM   RAM Cartridge (NEC) (Japan) (PC-6001mkII)" src="https://github.com/user-attachments/assets/5eed7ff5-71dc-468d-b674-8d7abbb30825" /><img width="30%" alt="Interior View 6 -  N60  PC-6007SR Kakuchou Kanji ROM   RAM Cartridge (NEC) (Japan) (PC-6001mkII)" src="https://github.com/user-attachments/assets/8b53ad58-0ae6-4924-ad9a-3d7ff81abd4c" />
## Unexpanded N62/N66 Kanji Repertoire
This subset of JIS Level 1 kanji is present in the PC-6001mkII / PC-6601 built-in kanji ROM; they are listed here with their JIS kuten codes:
```
1606 愛 …13 悪 …21 圧 …34 安 …37 暗 …38 案 …42 以 …44 位 …47 囲 …49 委 …53 意 …55 易 …59 異 …60 移 …63 胃 …65 衣 …68 遺 …69 医 …72 域 …73 育 …76 一 …77 壱 …81 茨 …85 印 …87 員 …88 因 …90 引 …91 飲
1701 院 …06 右 …07 宇 …09 羽 …11 雨 …31 運 …32 雲 …36 営 …39 映 …41 栄 …42 永 …43 泳 …49 英 …50 衛 …53 液 …55 益 …56 駅 …63 円 …64 園 …68 延 …72 沿 …73 演 …83 遠 …86 塩 …91 央 …93 往 …94 応
1803 横 …06 王 …11 黄 …12 岡 …13 沖 …15 億 …16 屋 …24 恩 …25 温 …27 音 …28 下 …29 化 …30 仮 …31 何 …33 価 …35 加 …36 可 …38 夏 …40 家 …42 科 …44 果 …46 歌 …47 河 …48 火 …54 花 …57 荷 …61 課 …63 貨 …65 過 …70 我 …72 画 …74 芽 …76 賀 …81 会 …82 解 …83 回 …87 快 …94 改
1903 械 …04 海 …05 灰 …06 界 …08 絵 …11 開 …12 階 …13 貝 …16 外 …18 害 …25 街 …38 各 …40 拡 …42 格 …46 確 …48 覚 …49 角 …53 閣 …55 革 …56 学 …58 楽 …59 額 …67 潟 …68 割 …72 活 …84 株
2008 寒 …09 刊 …11 勧 …12 巻 …16 完 …17 官 …19 干 …20 幹 …22 感 …23 慣 …31 歓 …33 漢 …39 看 …41 管 …42 簡 …49 観 …54 間 …56 関 …59 館 …61 丸 …63 岸 …67 眼 …68 岩 …73 顔 …74 願 …77 危 …78 喜 …79 器 …80 基 …83 寄 …84 岐 …85 希 …88 揮 …89 机 …90 旗 …92 期
2101 機 …02 帰 …04 気 …05 汽 …08 季 …10 紀 …12 規 …13 記 …14 貴 …15 起 …27 技 …31 疑 …33 義 …36 議 …50 客 …53 逆 …55 久 …57 休 …59 吸 …60 宮 …61 弓 …62 急 …63 救 …65 求 …67 泣 …69 球 …70 究 …73 級 …75 給 …76 旧 …77 牛 …78 去 …79 居 …83 挙 …86 許 …89 漁 …91 魚 …94 京
2201 供 …05 競 …06 共 …08 協 …13 境 …15 強 …21 教 …22 橋 …27 胸 …29 興 …31 郷 …32 鏡 …40 業 …41 局 …42 曲 …43 極 …44 玉 …48 勤 …49 均 …56 禁 …58 筋 …65 近 …66 金 …68 銀 …69 九 …71 句 …72 区 …76 苦 …81 具 …85 空
2307 熊 …15 君 …17 訓 …18 群 …19 軍 …20 郡 …24 係 …27 兄 …28 啓 …31 型 …33 形 …34 径 …41 敬 …42 景 …47 系 …48 経 …55 計 …57 警 …58 軽 …61 芸 …64 劇 …71 欠 …72 決 …73 潔 …74 穴 …75 結 …76 血 …78 月 …79 件 …82 健 …83 兼 …84 券 …90 建 …91 憲
2401 検 …02 権 …04 犬 …06 研 …08 絹 …09 県 …11 見 …17 険 …19 験 …21 元 …22 原 …23 厳 …26 減 …27 源 …29 現 …32 言 …34 限 …36 個 …37 古 …38 呼 …39 固 …42 己 …43 庫 …45 戸 …46 故 …48 湖 …62 五 …65 午 …69 後 …76 語 …77 誤 …78 護 …82 交 …85 候 …87 光 …88 公 …89 功 …90 効 …92 厚 …93 口 …94 向
2501 后 …05 好 …07 孝 …09 工 …12 幸 …13 広 …15 康 …27 校 …29 構 …33 港 …35 甲 …36 皇 …40 紅 …44 耕 …45 考 …50 航 …52 行 …54 講 …59 鉱 …61 鋼 …63 降 …65 香 …66 高 …70 号 …71 合 …79 刻 …80 告 …81 国 …82 穀 …85 黒 …92 骨
2603 今 …04 困 …12 根 …14 混 …20 佐 …24 左 …25 差 …26 査 …29 砂 …34 座 …38 再 …39 最 …42 妻 …45 才 …46 採 …49 済 …50 災 …55 祭 …57 細 …58 菜 …59 裁 …61 際 …63 在 …64 材 …65 罪 …66 財 …68 坂 …69 阪 …74 崎 …75 埼 …78 作 …82 昨 …86 策 …93 冊 …94 刷
2701 察 …05 札 …06 殺 …08 雑 …16 三 …18 参 …19 山 …22 散 …26 産 …27 算 …29 蚕 …31 賛 …32 酸 …36 残 …37 仕 …40 使 …42 司 …43 史 …45 四 …46 士 …47 始 …48 姉 …49 姿 …50 子 …52 市 …53 師 …54 志 …55 思 …56 指 …57 支 …63 止 …64 死 …65 氏 …68 私 …69 糸 …70 紙 …74 至 …75 視 …76 詞 …77 詩 …78 試 …79 誌 …81 資 …85 歯 …86 事 …87 似 …89 児 …90 字 …91 寺 …93 持 …94 時
2801 次 …02 滋 …03 治 …07 磁 …08 示 …10 耳 …11 自 …13 辞 …15 鹿 …16 式 …17 識 …23 七 …26 失 …28 室 …33 質 …34 実 …43 舎 …44 写 …45 射 …46 捨 …50 社 …52 者 …53 謝 …54 車 …58 借 …60 尺 …65 釈 …67 若 …69 弱 …71 主 …72 取 …73 守 …74 手 …79 種 …82 酒 …83 首 …85 受 …88 授 …89 樹 …91 需 …93 収 …94 周
2901 宗 …02 就 …03 州 …04 修 …06 拾 …09 秋 …10 終 …12 習 …16 衆 …21 週 …24 集 …27 住 …29 十 …30 従 …36 縦 …37 重 …41 宿 …43 祝 …44 縮 …47 熟 …48 出 …49 術 …50 述 …53 春 …64 準 …67 純 …71 順 …72 処 …73 初 …74 所 …75 暑 …80 署 …81 書 …84 諸 …85 助 …87 女 …88 序 …92 除 …93 傷
3001 勝 …06 商 …07 唱 …13 将 …14 小 …15 少 …21 承 …23 招 …28 昭 …35 消 …38 焼 …40 照 …42 省 …46 称 …47 章 …48 笑 …58 証 …61 象 …62 賞 …67 障 …69 上 …72 乗 …75 城 …76 場 …79 常 …80 情 …82 条 …85 状 …88 蒸
3102 植 …05 織 …06 職 …07 色 …09 食 …14 信 …20 心 …23 新 …25 森 …28 深 …29 申 …31 真 …32 神 …35 臣 …38 親 …40 身 …42 進 …43 針 …45 人 …46 仁 …62 図 …66 垂 …68 推 …69 水 …84 数
3203 寸 …04 世 …07 是 …09 制 …10 勢 …13 性 …14 成 …15 政 …16 整 …17 星 …18 晴 …21 正 …22 清 …24 生 …25 盛 …26 精 …27 聖 …28 声 …29 製 …30 西 …31 誠 …36 青 …37 静 …39 税 …42 席 …48 石 …49 積 …51 績 …53 責 …54 赤 …58 切 …60 接 …62 折 …63 設 …65 節 …66 説 …67 雪 …68 絶 …69 舌 …71 仙 …72 先 …73 千 …75 宣 …76 専 …78 川 …79 戦 …84 泉 …85 浅 …86 洗 …87 染 …94 線
3305 船 …10 選 …12 銭 …16 前 …17 善 …19 然 …20 全 …36 祖 …39 素 …40 組 …47 創 …50 倉 …53 奏 …56 層 …59 想 …64 操 …65 早 …72 争 …74 相 …75 窓 …77 総 …80 草 …86 走 …87 送 …92 像 …93 増
3401 臓 …02 蔵 …04 造 …06 側 …07 則 …09 息 …12 測 …13 足 …14 速 …15 俗 …16 属 …18 族 …19 続 …20 卒 …24 存 …25 孫 …26 尊 …27 損 …28 村 …30 他 …31 多 …32 太 …39 打 …46 体 …48 対 …51 帯 …52 待 …54 態 …63 貸 …64 退 …66 隊 …69 代 …70 台 …71 大 …72 第 …74 題 …80 宅
3503 達 …11 谷 …17 単 …20 担 …21 探 …26 炭 …27 短 …36 団 …39 断 …40 暖 …42 段 …43 男 …44 談 …45 値 …46 知 …47 地 …51 池 …54 置 …59 築 …61 竹 …67 茶 …69 着 …70 中 …71 仲 …72 宙 …73 忠 …75 昼 …76 柱 …77 注 …78 虫 …88 著 …89 貯 …90 丁 …91 兆
3602 帳 …03 庁 …05 張 …11 朝 …12 潮 …14 町 …18 腸 …20 調 …25 長 …26 頂 …27 鳥 …30 直 …34 賃 …37 津 …41 追 …43 痛 …44 通 …67 低 …68 停 …73 堤 …74 定 …76 底 …77 庭 …79 弟 …88 程
3708 敵 …10 的 …12 適 …20 鉄 …21 典 …23 天 …24 展 …25 店 …30 転 …32 点 …33 伝 …36 田 …37 電 …44 徒 …48 登 …52 都 …56 努 …57 度 …58 土 …62 党 …63 冬 …65 刀 …71 島 …74 投 …76 東 …82 湯 …85 燈 …86 当 …89 等 …90 答 …92 糖 …93 統
3804 討 …12 頭 …15 働 …16 動 …17 同 …18 堂 …19 導 …24 童 …27 道 …28 銅 …32 得 …33 徳 …35 特 …39 毒 …40 独 …41 読 …42 栃 …47 届 …64 奈 …65 那 …66 内 …76 縄 …78 南 …81 難 …83 二 …85 弐 …89 肉 …92 日 …93 乳 …94 入
3904 任 …07 認 …14 熱 …15 年 …16 念 …19 燃 …28 納 …29 能 …30 脳 …32 農 …38 覇 …40 波 …41 派 …43 破 …47 馬 …48 俳 …50 拝 …52 敗 …56 背 …57 肺 …59 配 …60 倍 …67 買 …68 売 …78 博 …82 白 …94 麦
4010 畑 …12 八 …15 発 …29 判 …30 半 …31 反 …36 板 …39 版 …40 犯 …41 班 …51 飯 …53 晩 …54 番 …61 否 …65 悲 …67 批 …70 比 …73 皮 …75 秘 …78 肥 …81 費 …83 非 …84 飛 …87 備 …94 美
4101 鼻 …12 必 …14 筆 …18 媛 …20 百 …22 俵 …24 標 …25 氷 …28 票 …29 表 …30 評 …34 病 …35 秒 …42 品 …47 貧 …52 不 …53 付 …55 夫 …56 婦 …57 富 …59 布 …60 府 …67 父 …73 負 …76 阜 …80 武 …84 部 …87 風 …91 副 …92 復 …94 服
4201 福 …02 腹 …03 複 …09 仏 …10 物 …12 分 …19 奮 …20 粉 …24 文 …25 聞 …28 兵 …31 平 …36 閉 …37 陛 …38 米 …44 別 …49 変 …50 片 …52 編 …53 辺 …54 返 …56 便 …57 勉 …59 弁 …61 保 …66 歩 …68 補 …72 墓 …76 母 …81 包 …83 報 …85 宝 …92 放 …93 方
4301 法 …12 訪 …13 豊 …20 亡 …26 忘 …29 暴 …30 望 …32 棒 …39 貿 …41 防 …44 北 …50 牧 …58 幌 …60 本 …69 妹 …71 枚 …72 毎 …75 幕 …86 末 …92 万 …94 満
4403 味 …04 未 …09 密 …14 脈 …17 民 …19 務 …21 無 …30 名 …31 命 …32 明 …33 盟 …34 迷 …36 鳴 …42 綿 …44 面 …47 模 …51 毛 …58 木 …60 目 …68 問 …71 門 …75 夜 …78 野 …80 矢 …82 役 …83 約 …84 薬 …85 訳 …93 油
4502 輸 …05 優 …06 勇 …07 友 …13 有 …19 由 …23 遊 …25 郵 …28 夕 …29 予 …30 余 …34 預 …36 幼 …38 容 …43 曜 …45 様 …46 洋 …49 用 …51 羊 …53 葉 …55 要 …59 陽 …60 養 …63 欲 …65 浴 …66 翌 …72 来 …78 落 …80 乱 …81 卵 …87 覧 …88 利 …92 梨 …93 理
4602 裏 …04 里 …06 陸 …07 律 …08 率 …09 立 …12 略 …14 流 …17 留 …25 旅 …30 両 …33 料 …41 良 …44 量 …46 領 …47 力 …48 緑 …51 林 …55 臨 …56 輪 …64 類 …65 令 …67 例 …68 冷 …73 礼 …82 歴 …83 列 …93 練
4702 連 …09 路 …11 労 …15 朗 …23 老 …27 六 …31 録 …32 論 …34 和 …35 話
```
