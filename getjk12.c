/*
 * getjk12 - MSX Kanji ROM saver
 * compile using:
 * zcc +cpm -o getjk12.com getjk12.c
 */

#include <stdio.h>
#include <stdlib.h>

unsigned char buf[64*32];

int main(int argc, char **argv) {
    if (argc != 1) {
        fprintf(
            stderr,
            "Usage: %s\nSaves KANJI ROM data to JISKAN1.ROM / JISKAN2.ROM\n",
            (argv[0] && *(argv[0])) ? argv[0] : "getjk12");
        fflush(stderr);
        exit(2);
    }
    puts("getjk12 - MSX Kanji ROM saver");
    for (int lvl = 0; lvl < 2; ++lvl) {
        char ofn[] = "JISKAN_.ROM";
        int p1 = 0xD8 | (lvl << 1);
        int p2 = p1 | 1;

        ofn[6] = '1' + lvl;
        printf("%s", ofn);
        fflush(stdout);
        {
            FILE *f = fopen(ofn, "wb");
            if (! f) {
                perror(ofn);
                exit(1);
            }
            for (int k=0; k<64; ++k) {
                outp(p2, k);
                for (int t=0; t<64; ++t) {
                    outp(p1, t);
                    for (int i=0; i<32; ++i) {
                       buf[(t << 5) | i] = inp(p2);
                    }
                }
                if ((fwrite(buf, 1, sizeof(buf), f) != sizeof(buf)) || fflush(f)) {
                    perror(ofn);
                    exit(1);
                }
                putchar('.');
            }
            if (fclose(f)) {
                perror(ofn);
                exit(1);
            }
            putchar('\n');
        }
    }
    return 0;
}