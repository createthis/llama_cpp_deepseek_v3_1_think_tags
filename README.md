# How

This was recorded with:

```bash
mitmdump --mode reverse:http://larry:11434 -p 8080 -w full_traffic.mitm
```

To install `mitmdump` so you can view this transcript: https://docs.mitmproxy.org/stable/overview/installation/

To view the entire conversation as plain text:

```bash
mitmdump -nr full_traffic.mitm --flow-detail 4
```

# What
I recorded several conversations between Open Hands AI and llama.cpp running DeepSeek V3.1 Q4_K_XL
using a tool called `mitmdump`.

# prompt

```
This is a test. Don't do anything, just respond with "ok" and finish the task.
```
