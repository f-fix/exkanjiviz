# exkanjiviz
quick-and-dirty visualizer for font data from:
- PC-6007SR Kakuchou Kanji ROM&RAM cartridge / 拡張漢字ＲＯＭ＆ＲＡＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-6601-01 Kakuchou Kanji ROM cartridge / 拡張漢字ＲＯＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-8801 series level 1 Kanji ROM `kanji1.rom`

## Usage
1. prepare your ROM image (either a real one, or a synthesized one) in `saverkanji` EXKANJI.ROM format
2. run `python exkanjiviz.py EXKANJI.ROM exkanji.png`
3. the created `exkanji.png` will have a visualization of the ROM contents laid out according to JIS ordering, which is not quite the same as the storage order

## ROM Data Extraction
If you need to get the data from your actual PC-6007SR cartridge or synthesize it from other font data, see the [おまけ：拡張漢字ROM
 section of the PC-6001mkII/6601用互換BASIC website](http://000.la.coocan.jp/p6/basic66.html#:~:text=%E5%A4%89%E6%8F%9B%E3%81%97%E3%81%9F%E4%BE%8B-,%E3%81%8A%E3%81%BE%E3%81%91%EF%BC%9A%E6%8B%A1%E5%BC%B5%E6%BC%A2%E5%AD%97ROM,-%E3%82%A8%E3%83%9F%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%BF%E3%81%A7%E3%81%AE). That page also links to a utility program that can convert both directions between `ksaver` EXTKANJI.ROM format and `saverkanji` EXKANJI.ROM format. I saved mine from the cartridge using a PC-6001mkII with [ksaver](https://web.archive.org/web/20071223192215/http://www.kisweb.ne.jp/personal/windy/pc6001/p6soft.html#ksaver) in EXTKANJI.ROM format and then converted it to EXKANJI.ROM format using the converter.

The `kanji1.rom` from the PC-8801 series has identical contents to PC-6007SR's Kanji ROM in saverkanji EXKANJI.ROM format.

ROM fingerprint information for the version dumped from my cartridge:

- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [ksaver EXTKANJI format].rom crc32:7e53b7d8 md5:1268ac01f5b3c38ef2be22576e54a6b6 sha1:827aadd671347a05281a3863e20dd9f31bff5423 sha256:85f212271e79c5a727e81ec61a8cba6fdeff0123e07a1bfcec71b769d8d532dc size:131072`
- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [saverkanji EXKANJI format].rom crc32:6178bd43 md5:d81c6d5d7ad1a4bbbd6ae22a01257603 sha1:82e11a177af6a5091dd67f50a2f4bafda84d6556 sha256:7608040cffb1951e5cc567abb63f75b5746777a1ba96196c1b75606b793bb4bb size:131072`
<img width="40%" alt="Front - [N60] 128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan)" src="https://github.com/user-attachments/assets/410fa46d-4063-4328-91a1-74a89bf85569" /><img width="40%" alt="Back - [N60] 128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan)" src="https://github.com/user-attachments/assets/29aa6621-edea-44e7-a241-475a20d6fa3f" />

## Example of the Visualization
Visualization of the contents of my PC-6007SR Kakuchou Kanji ROM & RAM Cartridge
<img width="4352" height="816" alt="[kanji visualization]" src="https://github.com/user-attachments/assets/2b8487bd-4525-483c-a981-6ba254e783f9" />
