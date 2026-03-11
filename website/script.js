(function () {
  var assetNamePattern = /^(open-dictate)-windows-v.+\.zip$/i;
  var releasesUrl = "https://github.com/tucaz/open-dictate/releases";
  var apiUrl = "https://api.github.com/repos/tucaz/open-dictate/releases/latest";
  var downloadLink = document.getElementById("download-link");
  var releaseNote = document.getElementById("release-note");
  var copyButton = document.getElementById("copy-install");
  var installCommand = document.getElementById("install-command");

  function setReleaseText(text) {
    if (releaseNote) {
      releaseNote.textContent = text;
    }
  }

  if (downloadLink) {
    downloadLink.href = releasesUrl;
  }

  if (copyButton && installCommand && navigator.clipboard) {
    copyButton.addEventListener("click", function () {
      navigator.clipboard.writeText(installCommand.textContent).then(function () {
        copyButton.textContent = "Copied";
        window.setTimeout(function () {
          copyButton.textContent = "Copy command";
        }, 1800);
      });
    });
  }

  fetch(apiUrl, {
    headers: {
      Accept: "application/vnd.github+json"
    }
  })
    .then(function (response) {
      if (!response.ok) {
        throw new Error("release lookup failed");
      }
      return response.json();
    })
    .then(function (release) {
      var asset = Array.isArray(release.assets)
        ? release.assets.find(function (item) {
            return assetNamePattern.test(item.name);
          })
        : null;

      if (asset && downloadLink) {
        downloadLink.href = asset.browser_download_url;
      }

      if (release && release.tag_name) {
        setReleaseText("Latest release: " + release.tag_name);
      } else {
        setReleaseText("Latest release available on GitHub Releases.");
      }
    })
    .catch(function () {
      setReleaseText("Could not resolve the latest release automatically. Using GitHub Releases.");
    });
})();
