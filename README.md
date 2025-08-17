# exkanjiviz
quick-and-dirty visualizer for font data from PC-6007SR Kakuchou Kanji ROM&amp;RAM cartridge / 拡張漢字ＲＡＭ＆ＲＯＭカートリッジ

## Usage
1. prepare your ROM image (either a real one, or a synthesized one) in `saverkanji` EXKANJI.ROM format
2. run `python exkanjiviz.py EXKANJI.ROM exkanji.png`
3. the creted `exkanji.png` will have a visualization of the ROM contents laid out according to JIS ordering, which is not quite the same as the storage order

If you need to get the data from your actual PC-6007SR cartridge or synthesize it from other font data, see the [おまけ：拡張漢字ROM
 section of the PC-6001mkII/6601用互換BASIC website](http://000.la.coocan.jp/p6/basic66.html#:~:text=%E5%A4%89%E6%8F%9B%E3%81%97%E3%81%9F%E4%BE%8B-,%E3%81%8A%E3%81%BE%E3%81%91%EF%BC%9A%E6%8B%A1%E5%BC%B5%E6%BC%A2%E5%AD%97ROM,-%E3%82%A8%E3%83%9F%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%BF%E3%81%A7%E3%81%AE). I saved mine from the cartridge using a PC-6001mkII with [ksaver](https://web.archive.org/web/20071223192215/http://www.kisweb.ne.jp/personal/windy/pc6001/p6soft.html#ksaver).

## Examples
Visualization of the contents of my PC-6007SR Kakuchou Kanji ROM & RAM Cartridge
<img width="4352" height="816" alt="image" src="https://github.com/user-attachments/assets/483740eb-65ea-4c14-82cd-d18ba5c1811d" />
