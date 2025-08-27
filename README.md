# Bundlegator

With just one command generate an RSS feed of all the new bundle deals offered by
[HumbleBundle](https://www.humblebundle.com/) and [Fanatical](https://www.fanatical.com/)
without needing to open a browser! Instead, simply redirect the contents to
your favorite RSS reader and enjoy all the important information in a neat format.

- [Requirements](#requirements)
- [Usage](#usage)
- [Install](#install)
- [Uninstall](#uninstall)

# Requirements

- go (1.24.5+)

# Usage

> [!IMPORTANT]
> Bundlegator is only meant to output an RSS feed and doesn't come with browsing functionality.
> For that I recommend the terminal RSS reader [Newsboat](https://github.com/newsboat/newsboat)
> or [Thunderbird](https://www.thunderbird.net/).

Running the binary will output the RSS feed to `stdout` which is perfect for
`Newsboat`. As per version 2.40, simply add this to your `~/.config/newsboat/urls` file:

```bash
"exec:~/path-to-binaries/bundlegator"
```

I haven't tried it for any other RSS reader, but for the ones that
don't support `stdin/stdout` I'd probably redirect the output to a file and
then set the RSS reader to read from that path.

```bash
bundlegator > file.rss
```

# Install

1. Ensure `$GOPATH` is setup correctly, and add it to your `$PATH` in your
`.bashrc` / `.zshrc` like so:

```bash
export GOPATH=$(go env GOPATH)
export GOBIN=$GOPATH/bin
export PATH=$PATH:$GOBIN
```

2. Install it by running:

```bash
go install github.com/el-damiano/bundlegator@latest
```

Or alternatively:

```bash
git clone https://github.com/el-damiano/bundlegator.git &&
cd bundlegator &&
go install .
```

# Uninstall

Either remove the file under `$GOBIN/bundlegator`, or go to where you have
cloned the repo and run:

```bash
go clean -i -cache -modcache
```
