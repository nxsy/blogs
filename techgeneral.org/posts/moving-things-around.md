title: Moving windows around
date: 2016-03-06 05:34:19
published: 2016-03-06 05:34:19
subtitle: Why can't they just stay where you want them?
description:
    Why can't they just stay where you want them?
created: !!timestamp 2016-03-06 05:34:19

While exploring the capabilities of [Open Broadcaster
Software](https://obsproject.com/), I noticed that I wanted to keep certain
windows at particular sizes, so that they fit full-screen in the video without
any resizing.  With a bit of space left over from the ostensible 1080p
broadcast, I also had some helper windows that I'd want to keep around but out
of the way.

Here's what I came up with as a proof of concept of finding windows by their
title, and setting their window sizes and position, depending on whether I want
their whole window (including chrome) to be sized that way, or just the inner
contents.

    :::cpp
    #include <windows.h>

    struct
    {
        const char *title_match;
        int width;
        int height;
        int left;
        int top;
        bool client_adjust;
    } matches[] =
    {
        {"GVIM", 1928, 1111, 0, 0, true},
        {"Microsoft Visual Studio", 1920, 1080, 0, 0, false},
        {"Open Broadcaster Software", 640, 640, 1920, 0, false},
    };

    int CALLBACK
    WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
    {
        HWND hwnd = 0;
        while ((hwnd = FindWindowEx(0, hwnd, 0, 0)) != 0)
        {
            char buffer[100];
            GetWindowText(hwnd, buffer, 100);

            WINDOWINFO info = {};
            info.cbSize = sizeof(info);
            GetWindowInfo(hwnd, &info);

            BOOL enabled = IsWindowEnabled(hwnd);
            BOOL visible = IsWindowVisible(hwnd);
            DWORD is_popup = info.dwStyle & WS_POPUP;

            if (enabled && visible && !is_popup)
            {
                for (auto &&m : matches)
                {
                    if (strstr(buffer, m.title_match))
                    {
                        RECT rect = {};
                        rect.left = m.left;
                        rect.top = m.top;
                        rect.right = m.width;
                        rect.bottom = m.height;
                        if (m.client_adjust)
                        {
                            AdjustWindowRectEx(&rect, info.dwStyle, 0, info.dwExStyle);
                        }
                        SetWindowPos(hwnd, 0, rect.left, rect.top, rect.right, rect.bottom, SWP_NOREPOSITION | SWP_NOZORDER);
                    }
                }
            }
        }
        return 0;
    }

