package de.tuda.stg.securecoder.plugin.settings;

import com.intellij.openapi.application.PathManager;
import com.intellij.openapi.diagnostic.Logger;
import com.intellij.openapi.progress.ProgressIndicator;
import com.intellij.openapi.util.SystemInfo;
import com.intellij.openapi.util.io.FileUtil;
import com.intellij.util.io.Decompressor;
import com.intellij.util.io.HttpRequests;
import de.tuda.stg.securecoder.plugin.SecureCoderBundle;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;

public class CodeQLInstaller {
    private static final Logger LOG = Logger.getInstance(CodeQLInstaller.class);

    private static final String FALLBACK_VERSION = "2.23.6";
    private static final String RELEASES_API_URL = "https://api.github.com/repos/github/codeql-cli-binaries/releases/latest";
    private static final String DOWNLOAD_BASE_URL = "https://github.com/github/codeql-cli-binaries/releases/download/v";

    public Path getOrInstallCodeQL(ProgressIndicator indicator) throws IOException {
        String version = resolveCodeQLVersion(indicator);
        Path installDir = Paths.get(PathManager.getSystemPath(), "codeql-tools", "codeql-dist-" + version);
        Path executable = getExecutablePath(installDir);

        if (Files.exists(executable)) {
            if (indicator != null) indicator.setText(SecureCoderBundle.INSTANCE.message("codeql.alreadyInstalled", version));
            return executable;
        }

        if (indicator != null) {
            indicator.setText(SecureCoderBundle.INSTANCE.message("codeql.downloading", version));
            indicator.setIndeterminate(true);
        }

        try {
            installCodeQL(version, installDir, indicator);
        } catch (IOException e) {
            FileUtil.delete(installDir.toFile());
            throw e;
        }

        if (!Files.exists(executable)) {
            throw new IOException(SecureCoderBundle.INSTANCE.message("codeql.installation.missingExecutable", executable.toString()));
        }

        return executable;
    }

    private String resolveCodeQLVersion(ProgressIndicator indicator) {
        if (indicator != null) indicator.setText(SecureCoderBundle.INSTANCE.message("codeql.checkingVersion"));
        try {
            return fetchLatestVersion();
        } catch (IOException e) {
            LOG.warn("Failed to fetch latest CodeQL version from GitHub API. Falling back to " + FALLBACK_VERSION, e);
            return FALLBACK_VERSION;
        }
    }

    private String fetchLatestVersion() throws IOException {
        return HttpRequests.request(RELEASES_API_URL)
                .accept("application/vnd.github.v3+json")
                .connect(request -> {
                    String response = request.readString(null);
                    Pattern pattern = Pattern.compile("\"tag_name\":\\s*\"v?([^\"]+)\"");
                    Matcher matcher = pattern.matcher(response);
                    if (matcher.find()) {
                        String version = matcher.group(1);
                        LOG.info("Detected latest CodeQL version: " + version);
                        return version;
                    }
                    throw new IOException("Could not parse version from GitHub API response");
                });
    }

    private void installCodeQL(String version, Path installDir, ProgressIndicator indicator) throws IOException {
        String downloadUrl = getDownloadUrl(version);
        LOG.info("Downloading CodeQL from: " + downloadUrl);

        File tempZip = FileUtil.createTempFile("codeql", ".zip");

        try {
            HttpRequests.request(downloadUrl).saveToFile(tempZip, indicator);
            if (indicator != null) indicator.setText(SecureCoderBundle.INSTANCE.message("codeql.extracting"));
            new Decompressor.Zip(tempZip).extract(installDir);
            Path executable = getExecutablePath(installDir);
            Path codeqlHome = installDir.resolve("codeql");
            Path mainBin = codeqlHome.resolve("codeql");
            setExecutablePermissions(mainBin);
            Path toolsDir = codeqlHome.resolve("tools");
            if (Files.exists(toolsDir)) {
                try (Stream<Path> stream = Files.walk(toolsDir)) {
                    stream.filter(p -> {
                        Path parent = p.getParent();
                        return parent != null && "bin".equals(parent.getFileName().toString()) && Files.isRegularFile(p);
                    }).forEach(this::setExecutablePermissions);
                } catch (IOException e) {
                    LOG.warn("Failed to walk tools directory for permissions: " + toolsDir.toString(), e);
                }
            }
            setExecutablePermissions(executable);
        } finally {
            FileUtil.delete(tempZip);
        }
    }

    private Path getExecutablePath(Path installDir) {
        Path binDir = installDir.resolve("codeql");
        return SystemInfo.isWindows
                ? binDir.resolve("codeql.exe")
                : binDir.resolve("codeql");
    }

    private String getDownloadUrl(String version) {
        String platform;
        if (SystemInfo.isWindows) {
            platform = "win64";
        } else if (SystemInfo.isMac) {
            platform = "osx64";
        } else if (SystemInfo.isLinux) {
            platform = "linux64";
        } else {
            throw new IllegalStateException("Unsupported operating system: " + SystemInfo.OS_NAME);
        }
        return DOWNLOAD_BASE_URL + version + "/codeql-" + platform + ".zip";
    }

    private void setExecutablePermissions(Path executable) {
        try {
            File file = executable.toFile();
            if (!file.setExecutable(true, true)) {
                throw new IOException("");
            }
        } catch (Exception e) {
            LOG.warn("Failed to set executable permissions for: " + executable, e);
        }
    }
}
