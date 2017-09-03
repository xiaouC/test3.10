#include "gen_fan_no_eyes.h"
#include "gen_fan_with_eyes.h"
#include "gen_wtt_no_eyes.h"
#include "gen_wtt_with_eyes.h"
#ifdef WIN32
#include <time.h>
#else
#include <sys/time.h>
#endif

void gen_data() {
	//gen_fan_no_eyes();          // 番牌 东南西北中发白
	//gen_fan_with_eyes();

	gen_wtt_no_eyes();        // 万条筒
	gen_wtt_with_eyes();
}

int main() {
#ifdef WIN32
	clock_t start, end;
	start = clock();
#else
	struct timeval start;
	struct timeval end;
	gettimeofday(&start, NULL);
#endif

    gen_data();

    // long long ss = 0;


    // int a = 2;
    // char s[10];
    // itoa(a, s, 2);
    // printf("2 : %s\n", s);

    //printf("sizeof(long long) = %lu\n", sizeof(long long));
    //int num[5] = { 111, 222, 333, 444, 555 };
    //long long ss = num[0];
    //printf("s = %lld\n", ss);
    //for (int i=1; i < 5; ++i) {
    //    ss = (ss<<10LL) + num[i];
    //    printf("s = %lld\n", ss);
    //}
    //printf("%lld\n", ss);
    //for (int i=0; i < 5; ++i) {
    //    int n = ss;
    //    n <<= 22;
    //    n >>= 22;
    //    ss >>= 10LL;
    //    printf("%d\n", n);
    //}

    //printf("sizeof(int) = %lu\n", sizeof(int));
    //int num1[3] = { 111, 222, 333 };
    //int s = num1[0];
    //printf("s = %d\n", s);
    //for (int i=1; i < 3; ++i) {
    //    s = (s<<10) + num1[i];
    //    printf("s = %d\n", s);
    //}
    //printf("%d\n", s);
    //for (int i=0; i < 3; ++i) {
    //    int n = s;
    //    n <<= 22;
    //    n >>= 22;
    //    s >>= 10;
    //    printf("%d\n", n);
    //}

#ifdef WIN32
	end = clock();
	float second = (float)(end - start) / CLOCKS_PER_SEC;
#else
	gettimeofday(&end, NULL);
	float second = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0f;
#endif

	printf("duration %f seconds.\n", second);

#ifdef WIN32
	getchar();
#endif

    return 0;
}
