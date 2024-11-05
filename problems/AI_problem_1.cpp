#include <iostream>
#include <bits/stdc++.h>
#define __GNUC__ 1 // in case you want more speed. It is not that much, honestly.

int empty_index = 0;
char frogs[202] = {0,};
int N = 0;
void move_left_frog_one_space()
{
    (void)std::swap(frogs[empty_index - 1], frogs[empty_index]);
    (void)printf("%s\n", frogs);
    empty_index--;
}

void move_left_frogs_jumps()
{
    while (empty_index > 1 && frogs[empty_index - 1] != '>' && frogs[empty_index - 2] == '>')
    {
        (void)std::swap(frogs[empty_index - 2], frogs[empty_index]);
        (void)printf("%s\n", frogs);
        empty_index -= 2;
    }
}

void move_right_frog_one_space()
{
    (void)std::swap(frogs[empty_index + 1], frogs[empty_index]);
    (void)printf("%s\n", frogs);
    empty_index++;
}

void move_right_frogs_jumps()
{
    while (empty_index < N*2 - 1 && frogs[empty_index + 1] != '<' && frogs[empty_index + 2] == '<')
    {
        (void)std::swap(frogs[empty_index + 2], frogs[empty_index]);
        (void)printf("%s\n", frogs);
        empty_index += 2;
    }
}

int main()
{
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);
    scanf("%d", &N);
    if (N < 2 && N > 100)
    {
        printf("Honestly, I am too lazy to implement better logic for UI. Restart.");
        return -1;
    }

    if (frogs == nullptr)
    {
        printf("No RAM, bruh? Restart.");
        return -1;
    }

    for (int i = 0; i < N; i++)
    {
        frogs[i] = '>';
        frogs[N*2-i] = '<';
    }
    frogs[N] = '_';
    empty_index = N;

    int do_times = N/2 + N%2;
    printf("%s\n", frogs);
    int i = 1;
    do
    {
        move_left_frogs_jumps();
        move_left_frog_one_space();
        move_right_frogs_jumps();

#if __GNUC__
        if (__builtin_expect((N*2 != empty_index), 1))
#else
        if (N*2 != empty_index)
#endif
        {
            move_right_frog_one_space();
        }

        i++;
    } while (i <= do_times);

    if (N%2 == 1)
    {
        move_left_frog_one_space();
    }

    i = 1;
    do_times = N/2;
    while ( i <= do_times)
    {
        move_left_frogs_jumps();
        move_right_frog_one_space();
        move_right_frogs_jumps();
        move_left_frog_one_space();
        i++;
    }

    return 0;
}
