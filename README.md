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

Using this script you can make a working PC-6001mkII / PC-6601 Kanji ROM from your Kakuchou Kanji ROM or PC-8801 Level 1 Kanji ROM. The PC-6001mkII and PC-6601 Kanji ROM contains a 1/8 subset of the Level 1 Kanji from PC-6007SR/PC-6601-01/PC-8801. Maybe we should call it Level 0.125 Kanji?

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
