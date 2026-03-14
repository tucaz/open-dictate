(function () {
  var assetNamePattern = /^(open-dictate)-windows-v.+\.zip$/i;
  var releasesUrl = "https://github.com/tucaz/open-dictate/releases";
  var apiUrl = "https://api.github.com/repos/tucaz/open-dictate/releases/latest";
  var zipLinks = document.querySelectorAll(".zip-release-link");
  var releaseNote = document.getElementById("release-note");
  var copyButton = document.getElementById("copy-install");
  var installCommand = document.getElementById("install-command");

  function setReleaseText(text) {
    if (releaseNote) {
      releaseNote.textContent = text;
    }
  }

  zipLinks.forEach(function (link) {
    link.href = releasesUrl;
  });

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

      if (asset) {
        zipLinks.forEach(function (link) {
          link.href = asset.browser_download_url;
        });
      }

      if (release && release.tag_name) {
        setReleaseText("Latest ZIP release: " + release.tag_name);
      } else {
        setReleaseText("Latest ZIP release available on GitHub Releases.");
      }
    })
    .catch(function () {
      setReleaseText("Could not resolve the latest ZIP release automatically. Using GitHub Releases.");
    });
})();
