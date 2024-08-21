# MIDI Controlled Player for Raspberry PI

Program Change messages will select a song bank.

Start messages will first play an audio file, and when playback is complete, it send a MIDI message to start the drum machine.

## dev steps

because I don't update this very often, and I forget...

First, find the process that automatically starts:

```
ps -ef | grep python
```

Next, stop it:

```
sudo kill -9 PROCESS_ID
```

With that process stopped, you can now start/stop as needed with:

```
python app.py
```

When you're all done, shut things down with:
```
TODO???
```

It appears that I run the git commands from the laptop and not the pi, but even then,
things don't always work the way I'd expect them to.
