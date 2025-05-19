# Python Flet - リリースと継続的インテグレーション（CI/CD）ガイド

このガイドでは、Python Fletで開発したマルチプラットフォームアプリケーションのためのCI/CDパイプラインの構築とリリースプロセスについて解説します。コードの品質管理からアプリストアへの公開までを効率的に自動化するための方法を学びましょう。

## 目次

1. [CI/CDの基本原則](#cicdの基本原則)
2. [継続的インテグレーション（CI）の設定](#継続的インテグレーションciの設定)
3. [継続的デリバリー（CD）の設定](#継続的デリバリーcdの設定)
4. [マルチプラットフォームビルドの自動化](#マルチプラットフォームビルドの自動化)
5. [自動テストの実行](#自動テストの実行)
6. [コード品質管理](#コード品質管理)
7. [バージョン管理とリリース戦略](#バージョン管理とリリース戦略)
8. [各ストアへの自動デプロイ](#各ストアへの自動デプロイ)
9. [CD環境の管理](#cd環境の管理)
10. [CI/CD実装例](#cicd実装例)

## CI/CDの基本原則

Fletアプリケーションにおける継続的インテグレーション・継続的デリバリーの基本原則：

### CI/CDの重要性
- コードの品質とテスト自動化による信頼性の向上
- リリースプロセスの迅速化と頻度の増加
- 開発チーム間のコラボレーション効率の向上
- 環境間の一貫性確保と問題の早期発見

### CI/CDパイプラインの基本構成
1. **コード変更**: 開発者がコードをリポジトリに反映
2. **ビルド**: アプリケーションをビルド
3. **テスト**: 自動テストを実行
4. **品質チェック**: コード品質検証を実施
5. **デプロイ**: 適切な環境にデプロイ（開発、テスト、本番）
6. **モニタリング**: リリース後の動作監視

### マルチプラットフォーム開発の課題
- 複数プラットフォーム（Android、iOS、Web）向けのビルド環境設定
- 各プラットフォーム固有の署名と配布プロセス
- クロスプラットフォームでの一貫したテスト実行
- 各アプリストアの審査プロセスと時間差への対応

## 継続的インテグレーション（CI）の設定

コードの継続的な統合とテストの自動化:

### GitHubActionsでのCI設定

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pytest pytest-cov black isort
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

    - name: Lint with flake8
      run: |
        flake8 app tests --count --max-complexity=10 --max-line-length=100 --statistics

    - name: Check code formatting with black
      run: |
        black --check app tests

    - name: Check import order with isort
      run: |
        isort --check-only --profile black app tests

    - name: Run tests and generate coverage report
      run: |
        pytest --cov=app --cov-report=xml

    - name: Upload coverage report
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### GitLabCIでのCI設定

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/

lint:
  stage: lint
  image: python:3.10-slim
  script:
    - pip install flake8 black isort
    - flake8 app tests --count --max-complexity=10 --max-line-length=100 --statistics
    - black --check app tests
    - isort --check-only --profile black app tests

test:
  stage: test
  image: python:3.10-slim
  script:
    - pip install pytest pytest-cov
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
    - pytest --cov=app --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: python:3.10-slim
  script:
    - pip install flet
    - pip install -r requirements.txt
    - flet build web --project-name ${CI_PROJECT_NAME}
  artifacts:
    paths:
      - build/web/
```

### Jenkinsfile

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.10-slim'
        }
    }

    stages {
        stage('Setup') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install flake8 pytest pytest-cov black isort'
                sh 'pip install -r requirements.txt'
                sh 'pip install -r requirements-dev.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'flake8 app tests --count --max-complexity=10 --max-line-length=100 --statistics'
                sh 'black --check app tests'
                sh 'isort --check-only --profile black app tests'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest --cov=app --cov-report=xml'
            }
            post {
                always {
                    junit 'test-reports/*.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }

        stage('Build') {
            steps {
                sh 'pip install flet'
                sh 'flet build web --project-name flet-app'
            }
            post {
                success {
                    archiveArtifacts artifacts: 'build/web/**', fingerprint: true
                }
            }
        }
    }
}
```

## 継続的デリバリー（CD）の設定

自動ビルドとデプロイのパイプライン構築:

### GitHub Actionsを使用したCD設定

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    tags:
      - 'v*'

jobs:
  build-web:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flet
        pip install -r requirements.txt

    - name: Build Web app
      run: |
        flet build web --project-name ${{ github.event.repository.name }}

    - name: Upload Web build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: web-build
        path: build/web/

    - name: Deploy to Firebase Hosting
      uses: FirebaseExtended/action-hosting-deploy@v0
      with:
        repoToken: '${{ secrets.GITHUB_TOKEN }}'
        firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
        channelId: live
        projectId: your-firebase-project-id

  build-android:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Java
      uses: actions/setup-java@v3
      with:
        distribution: 'zulu'
        java-version: '11'

    - name: Set up Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.7.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flet
        pip install -r requirements.txt

    - name: Build Android APK
      run: |
        flet build apk --release

    - name: Sign APK
      uses: r0adkll/sign-android-release@v1
      with:
        releaseDirectory: build/app/outputs/flutter-apk
        signingKeyBase64: ${{ secrets.SIGNING_KEY }}
        alias: ${{ secrets.KEY_ALIAS }}
        keyStorePassword: ${{ secrets.KEY_STORE_PASSWORD }}
        keyPassword: ${{ secrets.KEY_PASSWORD }}

    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: android-apk
        path: build/app/outputs/flutter-apk/app-release-signed.apk

    - name: Upload to Google Play
      uses: r0adkll/upload-google-play@v1
      with:
        serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
        packageName: com.example.fletapp
        releaseFiles: build/app/outputs/flutter-apk/app-release-signed.apk
        track: internal
        status: completed

  build-ios:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Set up Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.7.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flet
        pip install -r requirements.txt

    - name: Build iOS IPA
      run: |
        flet build ipa --release

    - name: Install Apple Certificate
      uses: apple-actions/import-codesign-certs@v1
      with:
        p12-file-base64: ${{ secrets.CERTIFICATES_P12 }}
        p12-password: ${{ secrets.CERTIFICATES_P12_PASSWORD }}

    - name: Upload IPA artifact
      uses: actions/upload-artifact@v3
      with:
        name: ios-ipa
        path: build/ios/ipa/

    - name: Upload to App Store Connect
      uses: Apple-Actions/upload-testflight-build@master
      with:
        app-path: build/ios/ipa/*.ipa
        issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
        api-key-id: ${{ secrets.APPSTORE_API_KEY_ID }}
        api-private-key: ${{ secrets.APPSTORE_API_PRIVATE_KEY }}
```

### Azure DevOpsパイプライン

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop
  tags:
    include:
    - v*

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.10'
  projectName: 'flet-app'

stages:
- stage: Test
  jobs:
  - job: TestAndLint
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
        addToPath: true

    - script: |
        python -m pip install --upgrade pip
        pip install flake8 pytest pytest-cov black isort
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
      displayName: 'Install dependencies'

    - script: |
        flake8 app tests
        black --check app tests
        isort --check-only --profile black app tests
      displayName: 'Run lint checks'

    - script: |
        pytest --cov=app --cov-report=xml
      displayName: 'Run tests'

    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: Cobertura
        summaryFileLocation: '$(System.DefaultWorkingDirectory)/coverage.xml'

- stage: BuildWeb
  dependsOn: Test
  condition: succeeded()
  jobs:
  - job: BuildAndDeploy
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
        addToPath: true

    - script: |
        pip install flet
        pip install -r requirements.txt
        flet build web --project-name $(projectName)
      displayName: 'Build Web app'

    - task: PublishBuildArtifacts@1
      inputs:
        pathtoPublish: 'build/web'
        artifactName: 'web-build'

    - task: AzureStaticWebApp@0
      inputs:
        app_location: 'build/web'
        api_location: ''
        output_location: ''
      env:
        AZURE_STATIC_WEB_APPS_API_TOKEN: $(AZURE_STATIC_WEB_APP_TOKEN)
      condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'))

- stage: BuildMobile
  dependsOn: Test
  condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'))
  jobs:
  - job: BuildAndroid
    steps:
    - task: JavaToolInstaller@0
      inputs:
        versionSpec: '11'
        jdkArchitectureOption: 'x64'
        jdkSourceOption: 'PreInstalled'

    - task: FlutterInstall@0
      inputs:
        channel: 'stable'
        version: 'latest'

    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
        addToPath: true

    - script: |
        pip install flet
        pip install -r requirements.txt
        flet build apk --release
      displayName: 'Build Android APK'

    - task: PublishBuildArtifacts@1
      inputs:
        pathtoPublish: 'build/app/outputs/flutter-apk'
        artifactName: 'android-apk'

  - job: BuildiOS
    pool:
      vmImage: 'macOS-latest'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
        addToPath: true

    - task: FlutterInstall@0
      inputs:
        channel: 'stable'
        version: 'latest'

    - script: |
        pip install flet
        pip install -r requirements.txt
        flet build ipa --release
      displayName: 'Build iOS IPA'

    - task: PublishBuildArtifacts@1
      inputs:
        pathtoPublish: 'build/ios/ipa'
        artifactName: 'ios-ipa'
```

## マルチプラットフォームビルドの自動化

各プラットフォーム向けのビルドプロセスの自動化:

### マルチプラットフォームビルドスクリプト

```python
# scripts/build_all.py
#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys
import platform

def run_command(command, cwd=None):
    """コマンドを実行し、結果を表示"""
    print(f"実行: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        print(f"エラー: コマンド {' '.join(command)} が失敗しました。")
        sys.exit(result.returncode)
    return result

def parse_args():
    """コマンドライン引数のパース"""
    parser = argparse.ArgumentParser(description='マルチプラットフォームビルドスクリプト')
    parser.add_argument('--version', help='アプリのバージョン', required=True)
    parser.add_argument('--build-number', help='ビルド番号', required=True)
    parser.add_argument('--platforms', help='ビルドするプラットフォーム (comma separated)',
                        default='web,android,ios,windows,macos,linux')
    parser.add_argument('--release', action='store_true', help='リリースビルドを作成')
    return parser.parse_args()

def setup_environment():
    """ビルド環境をセットアップ"""
    # 依存関係のインストール
    run_command(['pip', 'install', '-r', 'requirements.txt'])
    run_command(['pip', 'install', 'flet'])

    # Flutter SDKの確認
    try:
        run_command(['flutter', '--version'])
    except Exception:
        print("Flutter SDKが見つかりません。インストールしてください。")
        sys.exit(1)

def build_web(version, build_number, release=False):
    """Webアプリをビルド"""
    print("\n=== Webアプリのビルド開始 ===")

    cmd = [
        'flet',
        'build',
        'web',
        '--project-name', 'flet-app',
    ]

    if release:
        cmd.append('--release')

    # PWA設定
    cmd.extend(['--web-renderer', 'canvaskit', '--pwa'])

    # バージョン情報
    cmd.extend(['--version', version, '--build-number', build_number])

    run_command(cmd)
    print("=== Webアプリのビルド完了 ===")

    # ビルド成果物を確認
    web_output = os.path.join('build', 'web')
    if os.path.exists(web_output):
        print(f"Webビルド成果物: {web_output}")
    else:
        print("警告: Webビルド成果物が見つかりません")

def build_android(version, build_number, release=False):
    """Androidアプリをビルド"""
    print("\n=== Androidアプリのビルド開始 ===")

    cmd = [
        'flet',
        'build',
        'apk',
        '--project-name', 'flet-app',
    ]

    if release:
        cmd.append('--release')

    # アプリID設定
    cmd.extend(['--bundle-identifier', 'com.example.fletapp'])

    # バージョン情報
    cmd.extend(['--version', version, '--build-number', build_number])

    run_command(cmd)
    print("=== Androidアプリのビルド完了 ===")

    # ビルド成果物を確認
    apk_output = os.path.join('build', 'app', 'outputs', 'flutter-apk')
    if os.path.exists(apk_output):
        print(f"Androidビルド成果物: {apk_output}")
    else:
        print("警告: Androidビルド成果物が見つかりません")

def build_ios(version, build_number, release=False):
    """iOSアプリをビルド"""
    if platform.system() != 'Darwin':
        print("iOSビルドはmacOSでのみ可能です。スキップします。")
        return

    print("\n=== iOSアプリのビルド開始 ===")

    cmd = [
        'flet',
        'build',
        'ipa',
        '--project-name', 'flet-app',
    ]

    if release:
        cmd.append('--release')

    # アプリID設定
    cmd.extend(['--bundle-identifier', 'com.example.fletapp'])

    # バージョン情報
    cmd.extend(['--version', version, '--build-number', build_number])

    run_command(cmd)
    print("=== iOSアプリのビルド完了 ===")

    # ビルド成果物を確認
    ipa_output = os.path.join('build', 'ios', 'ipa')
    if os.path.exists(ipa_output):
        print(f"iOSビルド成果物: {ipa_output}")
    else:
        print("警告: iOSビルド成果物が見つかりません")

def build_windows(version, build_number, release=False):
    """Windowsアプリをビルド"""
    if platform.system() != 'Windows':
        print("Windowsビルドは、Windows環境でのみ可能です。スキップします。")
        return

    print("\n=== Windowsアプリのビルド開始 ===")

    cmd = [
        'flet',
        'build',
        'windows',
        '--project-name', 'flet-app',
    ]

    if release:
        cmd.append('--release')

    # バージョン情報
    cmd.extend(['--version', version, '--build-number', build_number])

    run_command(cmd)
    print("=== Windowsアプリのビルド完了 ===")

    # ビルド成果物を確認
    windows_output = os.path.join('build', 'windows')
    if os.path.exists(windows_output):
        print(f"Windowsビルド成果物: {windows_output}")
    else:
        print("警告: Windowsビルド成果物が見つかりません")

def build_macos(version, build_number, release=False):
    """macOSアプリをビルド"""
    if platform.system() != 'Darwin':
        print("macOSビルドは、macOS環境でのみ可能です。スキップします。")
        return

    print("\n=== macOSアプリのビルド開始 ===")

    cmd = [
        'flet',
        'build',
        'macos',
        '--project-name', 'flet-app',
    ]

    if release:
        cmd.append('--release')

    # アプリID設定
    cmd.extend(['--bundle-identifier', 'com.example.fletapp'])

    # バージョン情報
    cmd.extend(['--version', version, '--build-number', build_number])

    run_command(cmd)
    print("=== macOSアプリのビルド完了 ===")

    # ビルド成果物を確認
    macos_output = os.path.join('build', 'macos')
    if os.path.exists(macos_output):
        print(f"macOSビルド成果物: {macos_output}")
    else:
        print("警告: macOSビルド成果物が見つかりません")

def build_linux(version, build_number, release=False):
    """Linuxアプリをビルド"""
    if platform.system() != 'Linux':
        print("Linuxビルドは、Linux環境でのみ可能です。スキップします。")
        return

    print("\n=== Linuxアプリのビルド開始 ===")

    cmd = [
        'flet',
        'build',
        'linux',
        '--project-name', 'flet-app',
    ]

    if release:
        cmd.append('--release')

    # バージョン情報
    cmd.extend(['--version', version, '--build-number', build_number])

    run_command(cmd)
    print("=== Linuxアプリのビルド完了 ===")

    # ビルド成果物を確認
    linux_output = os.path.join('build', 'linux')
    if os.path.exists(linux_output):
        print(f"Linuxビルド成果物: {linux_output}")
    else:
        print("警告: Linuxビルド成果物が見つかりません")

def main():
    """メイン関数"""
    args = parse_args()
    platforms = args.platforms.split(',')

    print(f"ビルドバージョン: {args.version}")
    print(f"ビルド番号: {args.build_number}")
    print(f"ビルド対象プラットフォーム: {platforms}")
    print(f"リリースビルド: {'はい' if args.release else 'いいえ'}")

    # 環境セットアップ
    setup_environment()

    # 各プラットフォームのビルド
    if 'web' in platforms:
        build_web(args.version, args.build_number, args.release)

    if 'android' in platforms:
        build_android(args.version, args.build_number, args.release)

    if 'ios' in platforms:
        build_ios(args.version, args.build_number, args.release)

    if 'windows' in platforms:
        build_windows(args.version, args.build_number, args.release)

    if 'macos' in platforms:
        build_macos(args.version, args.build_number, args.release)

    if 'linux' in platforms:
        build_linux(args.version, args.build_number, args.release)

    print("\n=== 全ビルド完了 ===")

if __name__ == "__main__":
    main()
```

### コンテナ化されたビルド環境 (Dockerfile)

```dockerfile
# Dockerfile.build
FROM ubuntu:22.04

# タイムゾーン設定（インタラクティブなプロンプトを回避）
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    openjdk-11-jdk \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Flutter SDKのインストール
RUN git clone https://github.com/flutter/flutter.git /flutter
ENV PATH="/flutter/bin:${PATH}"
RUN flutter channel stable && flutter upgrade && flutter config --enable-web

# Android SDKのセットアップ
ENV ANDROID_SDK_ROOT="/opt/android-sdk"
ENV ANDROID_HOME="/opt/android-sdk"
ENV PATH="${PATH}:${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools"

# Android SDK のダウンロードとインストール
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools && \
    curl -o cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip && \
    unzip cmdline-tools.zip -d ${ANDROID_SDK_ROOT}/cmdline-tools && \
    mv ${ANDROID_SDK_ROOT}/cmdline-tools/cmdline-tools ${ANDROID_SDK_ROOT}/cmdline-tools/latest && \
    rm cmdline-tools.zip

# Android SDK コンポーネントのインストール
RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"

# Python環境の設定
RUN pip3 install --upgrade pip
RUN pip3 install flet

# ワーキングディレクトリの設定
WORKDIR /app

# エントリポイント
ENTRYPOINT ["python3", "scripts/build_all.py"]
```

### Docker Composeを使用したビルド

```yaml
# docker-compose.yml
version: '3'

services:
  build-android:
    build:
      context: .
      dockerfile: Dockerfile.build
    volumes:
      - .:/app
      - ${HOME}/.gradle:/root/.gradle
    command: ["--version", "1.0.0", "--build-number", "1", "--platforms", "android", "--release"]

  build-web:
    build:
      context: .
      dockerfile: Dockerfile.build
    volumes:
      - .:/app
    command: ["--version", "1.0.0", "--build-number", "1", "--platforms", "web", "--release"]
```

## 自動テストの実行

CI/CDパイプラインでの自動テスト実行と結果の処理:

### テスト自動化スクリプト

```python
# scripts/run_tests.py
#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys
import json
from datetime import datetime

def run_command(command, cwd=None):
    """コマンドを実行し、結果を返す"""
    print(f"実行: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return result

def parse_args():
    """コマンドライン引数のパース"""
    parser = argparse.ArgumentParser(description='テスト自動化スクリプト')
    parser.add_argument('--test-type', choices=['unit', 'integration', 'ui', 'all'], default='all',
                       help='実行するテストの種類')
    parser.add_argument('--report-dir', default='test-reports',
                       help='テストレポートの出力ディレクトリ')
    parser.add_argument('--coverage', action='store_true',
                       help='カバレッジレポートを生成する')
    parser.add_argument('--fail-fast', action='store_true',
                       help='最初の失敗で停止する')
    return parser.parse_args()

def setup_environment():
    """テスト環境をセットアップ"""
    # 依存関係のインストール
    result = run_command(['pip', 'install', '-r', 'requirements-dev.txt'])
    if result.returncode != 0:
        print(f"エラー: 依存関係のインストールに失敗しました。\n{result.stderr}")
        sys.exit(result.returncode)

def run_unit_tests(args):
    """ユニットテストを実行"""
    print("\n=== ユニットテスト実行 ===")

    cmd = ['pytest', 'tests/unit', '-v']

    if args.coverage:
        cmd.extend(['--cov=app', '--cov-report=xml:test-reports/coverage.xml',
                   '--cov-report=html:test-reports/coverage_html'])

    if args.fail_fast:
        cmd.append('-xvs')

    cmd.extend(['--junitxml', f'{args.report_dir}/unit-results.xml'])

    result = run_command(cmd)
    print(result.stdout)
    if result.returncode != 0:
        print(f"警告: ユニットテストが失敗しました。\n{result.stderr}")

    return result.returncode

def run_integration_tests(args):
    """インテグレーションテストを実行"""
    print("\n=== インテグレーションテスト実行 ===")

    cmd = ['pytest', 'tests/integration', '-v']

    if args.coverage:
        cmd.extend(['--cov=app', '--cov-report=xml:test-reports/coverage-integration.xml',
                   '--cov-report=html:test-reports/coverage_integration_html'])

    if args.fail_fast:
        cmd.append('-xvs')

    cmd.extend(['--junitxml', f'{args.report_dir}/integration-results.xml'])

    result = run_command(cmd)
    print(result.stdout)
    if result.returncode != 0:
        print(f"警告: インテグレーションテストが失敗しました。\n{result.stderr}")

    return result.returncode

def run_ui_tests(args):
    """UIテストを実行"""
    print("\n=== UIテスト実行 ===")

    cmd = ['pytest', 'tests/ui', '-v']

    if args.fail_fast:
        cmd.append('-xvs')

    cmd.extend(['--junitxml', f'{args.report_dir}/ui-results.xml'])

    result = run_command(cmd)
    print(result.stdout)
    if result.returncode != 0:
        print(f"警告: UIテストが失敗しました。\n{result.stderr}")

    return result.returncode

def generate_test_summary(args, results):
    """テスト結果のサマリーを生成"""
    print("\n=== テスト結果サマリー ===")

    summary = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "success": all(code == 0 for code in results.values())
    }

    # サマリーをJSONファイルに保存
    os.makedirs(args.report_dir, exist_ok=True)
    with open(f"{args.report_dir}/test-summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # コンソールに表示
    for test_type, result in results.items():
        status = "成功" if result == 0 else "失敗"
        print(f"{test_type}: {status}")

    print(f"\n全体結果: {'成功' if summary['success'] else '失敗'}")
    return summary['success']

def main():
    """メイン関数"""
    args = parse_args()

    # 出力ディレクトリを作成
    os.makedirs(args.report_dir, exist_ok=True)

    # 環境セットアップ
    setup_environment()

    results = {}

    # テスト実行
    if args.test_type in ['unit', 'all']:
        results['unit'] = run_unit_tests(args)
        if args.fail_fast and results['unit'] != 0:
            generate_test_summary(args, results)
            sys.exit(results['unit'])

    if args.test_type in ['integration', 'all']:
        results['integration'] = run_integration_tests(args)
        if args.fail_fast and results['integration'] != 0:
            generate_test_summary(args, results)
            sys.exit(results['integration'])

    if args.test_type in ['ui', 'all']:
        results['ui'] = run_ui_tests(args)
        if args.fail_fast and results['ui'] != 0:
            generate_test_summary(args, results)
            sys.exit(results['ui'])

    # 結果サマリー
    success = generate_test_summary(args, results)

    # 終了コード
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### GitHub Actions での並列テスト実行

```yaml
# .github/workflows/parallel-tests.yml
name: Parallel Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install lint dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black isort

    - name: Lint with flake8
      run: |
        flake8 app tests

    - name: Check formatting with black
      run: |
        black --check app tests

    - name: Check imports with isort
      run: |
        isort --check-only --profile black app tests

  unit-tests:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: [3.9, 3.10]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run unit tests
      run: |
        python scripts/run_tests.py --test-type unit --coverage --report-dir test-reports

    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: unit-test-results-${{ matrix.python-version }}
        path: test-reports/

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: test-reports/coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    needs: lint

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run integration tests
      run: |
        python scripts/run_tests.py --test-type integration --report-dir test-reports

    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: integration-test-results
        path: test-reports/

  ui-tests:
    runs-on: ubuntu-latest
    needs: lint

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run UI tests
      run: |
        python scripts/run_tests.py --test-type ui --report-dir test-reports

    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: ui-test-results
        path: test-reports/

  test-summary:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, ui-tests]
    if: always()

    steps:
    - uses: actions/checkout@v3

    - name: Download all test results
      uses: actions/download-artifact@v3
      with:
        path: artifacts

    - name: Generate test report
      run: |
        echo "# Test Results Summary" > report.md
        echo "" >> report.md
        echo "## Unit Tests" >> report.md
        cat artifacts/unit-test-results-3.10/test-summary.json >> report.md
        echo "" >> report.md
        echo "## Integration Tests" >> report.md
        cat artifacts/integration-test-results/test-summary.json >> report.md
        echo "" >> report.md
        echo "## UI Tests" >> report.md
        cat artifacts/ui-test-results/test-summary.json >> report.md

    - name: Upload combined report
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: report.md
```

## コード品質管理

静的解析と品質チェックの自動化:

### コード品質チェックスクリプト

```python
# scripts/check_code_quality.py
#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys
import json
from datetime import datetime

def run_command(command, cwd=None):
    """コマンドを実行し、結果を返す"""
    print(f"実行: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return result

def parse_args():
    """コマンドライン引数のパース"""
    parser = argparse.ArgumentParser(description='コード品質チェックスクリプト')
    parser.add_argument('--report-dir', default='quality-reports',
                       help='品質レポートの出力ディレクトリ')
    parser.add_argument('--fix', action='store_true',
                       help='可能な問題を自動修正する')
    parser.add_argument('--fail-on-error', action='store_true',
                       help='エラーがある場合に非ゼロ終了コードを返す')
    return parser.parse_args()

def setup_environment():
    """環境をセットアップ"""
    # 依存関係のインストール
    result = run_command(['pip', 'install', 'flake8', 'black', 'isort', 'pylint', 'bandit', 'mypy'])
    if result.returncode != 0:
        print(f"エラー: 依存関係のインストールに失敗しました。\n{result.stderr}")
        sys.exit(result.returncode)

def run_flake8(args):
    """flake8を実行"""
    print("\n=== flake8実行 ===")

    cmd = ['flake8', 'app', 'tests', '--count', '--max-complexity=10', '--max-line-length=100',
           '--statistics', f'--output-file={args.report_dir}/flake8.txt', '--tee']

    result = run_command(cmd)
    print(result.stdout)

    # エラー数をカウント
    error_count = 0
    if result.returncode != 0:
        try:
            # 最後の行からエラー数を抽出
            if result.stdout and result.stdout.strip():
                last_line = result.stdout.strip().split('\n')[-1]
                if last_line.isdigit():
                    error_count = int(last_line)
        except:
            error_count = -1  # カウント失敗

    return {
        "tool": "flake8",
        "success": result.returncode == 0,
        "error_count": error_count,
        "output": result.stdout
    }

def run_black(args):
    """blackを実行"""
    print("\n=== black実行 ===")

    cmd = ['black', '--check', 'app', 'tests']
    if args.fix:
        # --checkフラグを削除して実際に修正
        cmd.remove('--check')

    cmd.extend(['--verbose'])

    result = run_command(cmd)
    print(result.stdout)

    # 出力をファイルに保存
    with open(f"{args.report_dir}/black.txt", "w") as f:
        f.write(result.stdout)

    return {
        "tool": "black",
        "success": result.returncode == 0,
        "error_count": 0 if result.returncode == 0 else -1,  # blackは詳細なエラーカウントを提供しない
        "output": result.stdout
    }

def run_isort(args):
    """isortを実行"""
    print("\n=== isort実行 ===")

    cmd = ['isort', '--check-only', '--profile', 'black', 'app', 'tests']
    if args.fix:
        # --check-onlyフラグを削除して実際に修正
        cmd.remove('--check-only')

    cmd.extend(['--verbose'])

    result = run_command(cmd)
    print(result.stdout)

    # 出力をファイルに保存
    with open(f"{args.report_dir}/isort.txt", "w") as f:
        f.write(result.stdout)

    return {
        "tool": "isort",
        "success": result.returncode == 0,
        "error_count": 0 if result.returncode == 0 else -1,  # isortは詳細なエラーカウントを提供しない
        "output": result.stdout
    }

def run_pylint(args):
    """pylintを実行"""
    print("\n=== pylint実行 ===")

    cmd = ['pylint', 'app', '--output-format=text', f'--output={args.report_dir}/pylint.txt']

    result = run_command(cmd)
    rating = "?"

    # 評価を抽出
    for line in result.stdout.split('\n'):
        if "Your code has been rated at" in line:
            try:
                rating = line.split("Your code has been rated at ")[1].split('/')[0]
            except:
                pass

    print(f"Pylint評価: {rating}/10")

    return {
        "tool": "pylint",
        "success": result.returncode == 0,
        "rating": rating,
        "output": result.stdout
    }

def run_bandit(args):
    """bandit（セキュリティチェック）を実行"""
    print("\n=== bandit実行 ===")

    cmd = ['bandit', '-r', 'app', '-f', 'json', '-o', f'{args.report_dir}/bandit.json']

    result = run_command(cmd)

    # テキスト形式の出力も保存
    with open(f"{args.report_dir}/bandit.txt", "w") as f:
        f.write(result.stdout)

    issues_count = 0
    try:
        # JSONから問題数を抽出
        if os.path.exists(f"{args.report_dir}/bandit.json"):
            with open(f"{args.report_dir}/bandit.json", "r") as f:
                data = json.load(f)
                issues_count = len(data.get("results", []))
    except:
        pass

    success = result.returncode == 0
    print(f"セキュリティの問題: {issues_count}件")

    return {
        "tool": "bandit",
        "success": success,
        "issues_count": issues_count,
        "output": result.stdout
    }

def run_mypy(args):
    """mypy（型チェック）を実行"""
    print("\n=== mypy実行 ===")

    cmd = ['mypy', 'app', '--pretty']

    result = run_command(cmd)
    print(result.stdout)

    # 出力をファイルに保存
    with open(f"{args.report_dir}/mypy.txt", "w") as f:
        f.write(result.stdout)

    return {
        "tool": "mypy",
        "success": result.returncode == 0,
        "output": result.stdout
    }

def generate_quality_summary(args, results):
    """品質チェック結果のサマリーを生成"""
    print("\n=== コード品質チェック結果サマリー ===")

    summary = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "success": all(r.get("success", False) for r in results)
    }

    # サマリーをJSONファイルに保存
    with open(f"{args.report_dir}/quality-summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Markdown形式のレポートを生成
    with open(f"{args.report_dir}/quality-report.md", "w") as f:
        f.write("# コード品質レポート\n\n")
        f.write(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## サマリー\n\n")
        f.write(f"全体結果: {'成功' if summary['success'] else '失敗'}\n\n")

        f.write("| ツール | 結果 | 詳細 |\n")
        f.write("|--------|------|------|\n")

        for result in results:
            tool = result["tool"]
            success = "✅" if result.get("success", False) else "❌"
            details = ""

            if tool == "flake8":
                details = f"エラー数: {result.get('error_count', 0)}"
            elif tool == "pylint":
                details = f"評価: {result.get('rating', '?')}/10"
            elif tool == "bandit":
                details = f"セキュリティの問題: {result.get('issues_count', 0)}件"

            f.write(f"| {tool} | {success} | {details} |\n")

    # コンソールに表示
    for result in results:
        tool = result["tool"]
        success = "成功" if result.get("success", False) else "失敗"
        print(f"{tool}: {success}")

    print(f"\n全体結果: {'成功' if summary['success'] else '失敗'}")
    return summary['success']

def main():
    """メイン関数"""
    args = parse_args()

    # 出力ディレクトリを作成
    os.makedirs(args.report_dir, exist_ok=True)

    # 環境セットアップ
    setup_environment()

    results = []

    # 各ツールを実行
    results.append(run_flake8(args))
    results.append(run_black(args))
    results.append(run_isort(args))
    results.append(run_pylint(args))
    results.append(run_bandit(args))
    results.append(run_mypy(args))

    # 結果サマリー
    success = generate_quality_summary(args, results)

    # 終了コード
    if args.fail_on_error and not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### SonarQubeとの統合（GitHub Actions）

```yaml
# .github/workflows/sonarqube.yml
name: SonarQube Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  sonarqube:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests with coverage
      run: |
        pytest --cov=app --cov-report=xml

    - name: SonarQube Scan
      uses: SonarSource/sonarqube-scan-action@master
      env:
        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      with:
        args: >
          -Dsonar.projectName=flet-app
          -Dsonar.projectKey=flet-app
          -Dsonar.python.coverage.reportPaths=coverage.xml
          -Dsonar.sources=app
          -Dsonar.tests=tests
```

### GitHook設定スクリプト

```python
# scripts/setup_git_hooks.py
#!/usr/bin/env python3
import os
import sys
import stat

def create_pre_commit_hook():
    """pre-commitフックを作成"""
    hook_path = os.path.join('.git', 'hooks', 'pre-commit')

    # フックの内容
    hook_content = """#!/bin/bash
set -e

echo "Running pre-commit checks..."

# コードフォーマットをチェック
echo "Checking code format with black..."
python -m black --check app tests

# importの順序をチェック
echo "Checking import order with isort..."
python -m isort --check-only --profile black app tests

# Lintをチェック
echo "Linting with flake8..."
python -m flake8 app tests --count --max-complexity=10 --max-line-length=100 --statistics

# セキュリティチェック
echo "Running security checks with bandit..."
python -m bandit -r app

echo "All checks passed!"
"""

    # フックファイルを作成
    with open(hook_path, 'w') as f:
        f.write(hook_content)

    # 実行権限を付与
    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"pre-commitフックを作成しました: {hook_path}")

def create_pre_push_hook():
    """pre-pushフックを作成"""
    hook_path = os.path.join('.git', 'hooks', 'pre-push')

    # フックの内容
    hook_content = """#!/bin/bash
set -e

echo "Running pre-push checks..."

# テストを実行
echo "Running tests..."
python -m pytest

echo "All tests passed!"
"""

    # フックファイルを作成
    with open(hook_path, 'w') as f:
        f.write(hook_content)

    # 実行権限を付与
    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"pre-pushフックを作成しました: {hook_path}")

def setup_hooks():
    """すべてのGitフックをセットアップ"""
    # .gitディレクトリの確認
    if not os.path.isdir('.git'):
        print("エラー: .gitディレクトリが見つかりません。Gitリポジトリのルートで実行してください。")
        sys.exit(1)

    # hooksディレクトリが存在することを確認
    hooks_dir = os.path.join('.git', 'hooks')
    if not os.path.isdir(hooks_dir):
        os.makedirs(hooks_dir)

    # 各フックを作成
    create_pre_commit_hook()
    create_pre_push_hook()

    print("\nGitフックのセットアップが完了しました！")
    print("これらのフックは、コミット時やプッシュ時に自動的に実行されます。")

if __name__ == "__main__":
    setup_hooks()
```

## バージョン管理とリリース戦略

効率的なバージョニングとリリース管理:

### セマンティックバージョニングスクリプト

```python
# scripts/version_manager.py
#!/usr/bin/env python3
import os
import re
import sys
import argparse
import json
import subprocess
from datetime import datetime

VERSION_FILE = "app/core/version.py"
CHANGELOG_FILE = "CHANGELOG.md"

def run_command(command):
    """コマンドを実行し、結果を返す"""
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description='バージョン管理スクリプト')

    subparsers = parser.add_subparsers(dest='command', help='コマンド')

    # 現在のバージョンを表示
    current_parser = subparsers.add_parser('current', help='現在のバージョンを表示')

    # バージョンを更新
    bump_parser = subparsers.add_parser('bump', help='バージョンを更新')
    bump_parser.add_argument('type', choices=['major', 'minor', 'patch'],
                          help='更新するバージョン部分')
    bump_parser.add_argument('--dry-run', action='store_true',
                          help='実際には更新せず、結果だけ表示')

    # リリースを作成
    release_parser = subparsers.add_parser('release', help='リリースを作成')
    release_parser.add_argument('--dry-run', action='store_true',
                             help='実際には更新せず、結果だけ表示')

    # チェンジログを生成/更新
    changelog_parser = subparsers.add_parser('changelog', help='チェンジログを生成/更新')
    changelog_parser.add_argument('--since', help='指定したタグ以降のコミットを含める')

    return parser.parse_args()

def get_current_version():
    """現在のバージョンを取得"""
    if not os.path.exists(VERSION_FILE):
        print(f"エラー: バージョンファイル {VERSION_FILE} が見つかりません")
        return None

    with open(VERSION_FILE, 'r') as f:
        content = f.read()

    match = re.search(r'VERSION\s*=\s*[\'"](.+)[\'"]', content)
    if match:
        return match.group(1)
    else:
        print(f"エラー: {VERSION_FILE} からバージョン情報を取得できませんでした")
        return None

def update_version_file(new_version, dry_run=False):
    """バージョンファイルを更新"""
    if not os.path.exists(VERSION_FILE):
        print(f"エラー: バージョンファイル {VERSION_FILE} が見つかりません")
        return False

    with open(VERSION_FILE, 'r') as f:
        content = f.read()

    # バージョン番号を更新
    new_content = re.sub(
        r'(VERSION\s*=\s*[\'"]).+([\'"]\s*)',
        r'\g<1>{}\g<2>'.format(new_version),
        content
    )

    # ビルド日時も更新
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_content = re.sub(
        r'(BUILD_DATE\s*=\s*[\'"]).+([\'"]\s*)',
        r'\g<1>{}\g<2>'.format(now),
        new_content
    )

    if dry_run:
        print(f"[DRY-RUN] バージョンを {new_version} に更新します")
        print(f"[DRY-RUN] ビルド日時を {now} に更新します")
        return True

    # ファイルに書き込み
    with open(VERSION_FILE, 'w') as f:
        f.write(new_content)

    print(f"バージョンを {new_version} に更新しました")
    print(f"ビルド日時を {now} に更新しました")
    return True

def bump_version(version_type, dry_run=False):
    """バージョンを更新"""
    current = get_current_version()
    if not current:
        return False

    # バージョン番号を分解
    try:
        major, minor, patch = map(int, current.split('.'))
    except ValueError:
        print(f"エラー: 現在のバージョン {current} が semantic versioning 形式ではありません")
        return False

    # バージョンタイプに応じて更新
    if version_type == 'major':
        new_version = f"{major + 1}.0.0"
    elif version_type == 'minor':
        new_version = f"{major}.{minor + 1}.0"
    elif version_type == 'patch':
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        print(f"エラー: 不明なバージョンタイプ: {version_type}")
        return False

    # バージョンファイルを更新
    if not update_version_file(new_version, dry_run):
        return False

    return True

def create_git_tag(version, dry_run=False):
    """Gitタグを作成"""
    tag_name = f"v{version}"

    # タグが既に存在するか確認
    result = run_command(f"git tag -l {tag_name}")
    if tag_name in result.stdout:
        print(f"エラー: タグ {tag_name} は既に存在します")
        return False

    # 変更をコミット
    if not dry_run:
        # まず変更されたファイルを追加
        run_command(f"git add {VERSION_FILE}")

        # チェンジログが更新されていれば追加
        if os.path.exists(CHANGELOG_FILE):
            run_command(f"git add {CHANGELOG_FILE}")

        # バージョン更新をコミット
        commit_result = run_command(f'git commit -m "バージョン {version} にアップデート"')
        if commit_result.returncode != 0:
            print(f"エラー: コミットに失敗しました: {commit_result.stderr}")
            return False

        # タグを作成
        tag_result = run_command(f'git tag -a {tag_name} -m "バージョン {version}"')
        if tag_result.returncode != 0:
            print(f"エラー: タグ作成に失敗しました: {tag_result.stderr}")
            return False

        print(f"タグ {tag_name} を作成しました")
    else:
        print(f"[DRY-RUN] タグ {tag_name} を作成します")

    return True

def generate_changelog(since=None):
    """チェンジログを生成/更新"""
    current = get_current_version()
    if not current:
        return False

    # 変更履歴を収集
    if since:
        result = run_command(f"git log {since}..HEAD --pretty=format:'%h %s' --no-merges")
    else:
        # 既存のタグを確認
        tags_result = run_command("git tag -l 'v*' --sort=-v:refname")
        tags = tags_result.stdout.strip().split('\n')

        if tags and tags[0]:
            # 最新のタグからの変更を収集
            result = run_command(f"git log {tags[0]}..HEAD --pretty=format:'%h %s' --no-merges")
        else:
            # タグがなければすべての履歴を収集
            result = run_command("git log --pretty=format:'%h %s' --no-merges")

    commits = result.stdout.strip().split('\n')

    # コミットを分類
    features = []
    fixes = []
    others = []

    for commit in commits:
        if not commit:
            continue

        if "fix:" in commit.lower() or "修正:" in commit:
            fixes.append(commit)
        elif "feat:" in commit.lower() or "機能:" in commit:
            features.append(commit)
        else:
            others.append(commit)

    # チェンジログを作成/更新
    now = datetime.now().strftime("%Y-%m-%d")
    changelog_entry = f"## {current} ({now})\n\n"

    if features:
        changelog_entry += "### 新機能\n\n"
        for feat in features:
            changelog_entry += f"- {feat}\n"
        changelog_entry += "\n"

    if fixes:
        changelog_entry += "### バグ修正\n\n"
        for fix in fixes:
            changelog_entry += f"- {fix}\n"
        changelog_entry += "\n"

    if others:
        changelog_entry += "### その他の変更\n\n"
        for other in others:
            changelog_entry += f"- {other}\n"
        changelog_entry += "\n"

    # ファイルを更新
    if os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        # ファイルの先頭に追加
        if content.startswith("# "):
            # ヘッダーがある場合は、ヘッダーの後に追加
            header_end = content.find('\n', 0)
            new_content = content[:header_end + 1] + "\n" + changelog_entry + content[header_end + 1:]
        else:
            # ヘッダーがない場合は、ファイルの先頭に追加
            new_content = changelog_entry + content
    else:
        # ファイルが存在しない場合は新規作成
        new_content = "# 変更履歴\n\n" + changelog_entry

    with open(CHANGELOG_FILE, 'w') as f:
        f.write(new_content)

    print(f"チェンジログを更新しました: {CHANGELOG_FILE}")
    return True

def create_release(dry_run=False):
    """リリースを作成"""
    current = get_current_version()
    if not current:
        return False

    # チェンジログを生成
    if not generate_changelog():
        print("警告: チェンジログの生成に失敗しました")

    # Gitタグを作成
    if not create_git_tag(current, dry_run):
        return False

    if not dry_run:
        # タグをリモートにプッシュ
        push_result = run_command("git push --follow-tags")
        if push_result.returncode != 0:
            print(f"エラー: プッシュに失敗しました: {push_result.stderr}")
            return False

        print("変更をリモートにプッシュしました")
    else:
        print("[DRY-RUN] 変更をリモートにプッシュします")

    return True

def main():
    """メイン関数"""
    args = parse_args()

    if args.command == 'current':
        # 現在のバージョンを表示
        current = get_current_version()
        if current:
            print(f"現在のバージョン: {current}")
        return current is not None

    elif args.command == 'bump':
        # バージョンを更新
        if bump_version(args.type, args.dry_run):
            print(f"{args.type} バージョンの更新が完了しました")
            return True
        return False

    elif args.command == 'release':
        # リリースを作成
        if create_release(args.dry_run):
            print("リリース作成が完了しました")
            return True
        return False

    elif args.command == 'changelog':
        # チェンジログを生成/更新
        if generate_changelog(args.since):
            print("チェンジログの生成が完了しました")
            return True
        return False

    else:
        print("コマンドを指定してください。ヘルプを表示するには -h を使用してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### リリースチェックリスト

```markdown
# リリースチェックリスト

## バージョン情報
- [ ] バージョン番号の確認: `python scripts/version_manager.py current`
- [ ] バージョン番号の更新: `python scripts/version_manager.py bump [major|minor|patch]`
- [ ] チェンジログの更新: `python scripts/version_manager.py changelog`

## 前提条件
- [ ] すべてのテストが通過している: `pytest`
- [ ] コード品質チェックに問題がない: `python scripts/check_code_quality.py`
- [ ] ドキュメントが最新である

## ビルド検証
- [ ] Webビルドの確認
- [ ] Androidビルドの確認
- [ ] iOSビルドの確認
- [ ] 必要に応じてデスクトップビルド（Windows/macOS/Linux）の確認

## 機能検証
- [ ] 主要機能のテスト
- [ ] 新機能のテスト
- [ ] 修正されたバグの検証
- [ ] パフォーマンステスト
- [ ] 多言語対応の確認

## セキュリティ
- [ ] セキュリティ脆弱性のスキャン: `bandit -r app`
- [ ] 依存関係の脆弱性チェック: `pip-audit`
- [ ] リリースビルドのセキュリティ設定を確認

## ドキュメント
- [ ] README.mdの更新
- [ ] CHANGELOG.mdの更新
- [ ] ユーザーマニュアルの更新
- [ ] API/開発者ドキュメントの更新

## リリースプロセス
- [ ] リリースブランチの作成: `git checkout -b release/vX.Y.Z`
- [ ] 最終バージョン更新のコミット: `git commit -am "バージョンX.Y.Zにアップデート"`
- [ ] リリースタグの作成: `git tag -a vX.Y.Z -m "バージョンX.Y.Z"`
- [ ] `main`ブランチへのマージ: `git checkout main && git merge release/vX.Y.Z`
- [ ] リモートへのプッシュ: `git push origin main --tags`
- [ ] `develop`ブランチへの変更のバックポート: `git checkout develop && git merge main && git push origin develop`

## デプロイ
- [ ] Webアプリのデプロイ
- [ ] Google Play Storeへの提出
- [ ] Apple App Storeへの提出
- [ ] ユーザーへの通知
```

## 各ストアへの自動デプロイ

アプリストアへの自動デプロイの設定:

### Google Play Storeへの自動デプロイ

```yaml
# .github/workflows/deploy-google-play.yml
name: Deploy to Google Play

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Extract version from tag
      id: get_version
      run: |
        VERSION=${GITHUB_REF#refs/tags/v}
        echo "version=$VERSION" >> $GITHUB_OUTPUT
        # ビルド番号として日付とコミット短縮ハッシュを使用
        BUILD_NUMBER=$(date +%Y%m%d)$(git rev-parse --short HEAD)
        echo "build_number=$BUILD_NUMBER" >> $GITHUB_OUTPUT

    - name: Set up Java
      uses: actions/setup-java@v3
      with:
        distribution: 'zulu'
        java-version: '11'

    - name: Set up Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.7.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flet
        pip install -r requirements.txt

    - name: Build Android App Bundle
      run: |
        flet build appbundle \
          --project-name flet-app \
          --release \
          --version ${{ steps.get_version.outputs.version }} \
          --build-number ${{ steps.get_version.outputs.build_number }} \
          --bundle-identifier com.example.fletapp

    - name: Setup Google Play signing
      env:
        SIGNING_KEY_BASE64: ${{ secrets.SIGNING_KEY_BASE64 }}
        KEY_STORE_PASSWORD: ${{ secrets.KEY_STORE_PASSWORD }}
        KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
      run: |
        # Decode the base64 encoded key to a file
        echo $SIGNING_KEY_BASE64 | base64 --decode > keystore.jks

        # 署名設定
        cat >> android/key.properties << EOF
        storePassword=$KEY_STORE_PASSWORD
        keyPassword=$KEY_PASSWORD
        keyAlias=$KEY_ALIAS
        storeFile=$(pwd)/keystore.jks
        EOF

    - name: Sign App Bundle
      uses: r0adkll/sign-android-release@v1
      id: sign_app
      with:
        releaseDirectory: build/app/outputs/bundle/release
        signingKeyBase64: ${{ secrets.SIGNING_KEY_BASE64 }}
        alias: ${{ secrets.KEY_ALIAS }}
        keyStorePassword: ${{ secrets.KEY_STORE_PASSWORD }}
        keyPassword: ${{ secrets.KEY_PASSWORD }}
      env:
        BUILD_TOOLS_VERSION: "33.0.0"

    - name: Upload to Google Play
      uses: r0adkll/upload-google-play@v1
      with:
        serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
        packageName: com.example.fletapp
        releaseFiles: ${{steps.sign_app.outputs.signedReleaseFile}}
        track: production
        status: completed
        whatsNewDirectory: distribution/whatsnew
        mappingFile: build/app/outputs/mapping/release/mapping.txt
```

### Apple App Storeへの自動デプロイ

```yaml
# .github/workflows/deploy-app-store.yml
name: Deploy to App Store

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-deploy:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3

    - name: Extract version from tag
      id: get_version
      run: |
        VERSION=${GITHUB_REF#refs/tags/v}
        echo "version=$VERSION" >> $GITHUB_OUTPUT
        # ビルド番号として日付とコミット短縮ハッシュを使用
        BUILD_NUMBER=$(date +%Y%m%d)$(git rev-parse --short HEAD)
        echo "build_number=$BUILD_NUMBER" >> $GITHUB_OUTPUT

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Set up Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.7.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flet
        pip install -r requirements.txt

    - name: Install Apple Certificate
      uses: apple-actions/import-codesign-certs@v1
      with:
        p12-file-base64: ${{ secrets.CERTIFICATES_P12 }}
        p12-password: ${{ secrets.CERTIFICATES_P12_PASSWORD }}
        keychain: build
        keychain-password: ${{ secrets.KEYCHAIN_PASSWORD }}

    - name: Install provisioning profile
      run: |
        mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
        echo "${{ secrets.PROVISIONING_PROFILE }}" | base64 --decode > ~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision

    - name: Build iOS app
      run: |
        flet build ipa \
          --project-name flet-app \
          --release \
          --version ${{ steps.get_version.outputs.version }} \
          --build-number ${{ steps.get_version.outputs.build_number }} \
          --bundle-identifier com.example.fletapp

    - name: Upload to App Store Connect
      env:
        APP_STORE_CONNECT_USERNAME: ${{ secrets.APP_STORE_CONNECT_USERNAME }}
        APP_STORE_CONNECT_PASSWORD: ${{ secrets.APP_STORE_CONNECT_PASSWORD }}
      run: |
        xcrun altool --upload-app --type ios --file build/ios/ipa/*.ipa \
          --username "$APP_STORE_CONNECT_USERNAME" \
          --password "$APP_STORE_CONNECT_PASSWORD"

    # または App Store Connect APIを使用
    - name: Upload to App Store Connect API
      uses: Apple-Actions/upload-testflight-build@master
      with:
        app-path: build/ios/ipa/*.ipa
        issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
        api-key-id: ${{ secrets.APPSTORE_API_KEY_ID }}
        api-private-key: ${{ secrets.APPSTORE_API_PRIVATE_KEY }}
```

### Webアプリのデプロイ（Firebase Hosting）

```yaml
# .github/workflows/deploy-web.yml
name: Deploy Web App

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Extract version from tag
      id: get_version
      run: |
        VERSION=${GITHUB_REF#refs/tags/v}
        echo "version=$VERSION" >> $GITHUB_OUTPUT
        # ビルド番号として日付とコミット短縮ハッシュを使用
        BUILD_NUMBER=$(date +%Y%m%d)$(git rev-parse --short HEAD)
        echo "build_number=$BUILD_NUMBER" >> $GITHUB_OUTPUT

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flet
        pip install -r requirements.txt

    - name: Build Web app
      run: |
        flet build web \
          --project-name flet-app \
          --web-renderer canvaskit \
          --pwa \
          --version ${{ steps.get_version.outputs.version }} \
          --build-number ${{ steps.get_version.outputs.build_number }}

    # Firebase Hostingへのデプロイ
    - name: Deploy to Firebase Hosting
      uses: FirebaseExtended/action-hosting-deploy@v0
      with:
        repoToken: '${{ secrets.GITHUB_TOKEN }}'
        firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
        channelId: live
        projectId: your-firebase-project-id
        target: production  # Firebase target名（複数サイトがある場合）
```

## CD環境の管理

継続的デリバリー環境の管理とシークレットの取り扱い:

### シークレット管理スクリプト

```python
# scripts/setup_secrets.py
#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import base64
from getpass import getpass

def parse_args():
    """コマンドライン引数のパース"""
    parser = argparse.ArgumentParser(description='CI/CDシークレット管理スクリプト')

    subparsers = parser.add_subparsers(dest='command', help='コマンド')

    # GitHubシークレットを設定
    github_parser = subparsers.add_parser('github', help='GitHub Actionsのシークレットを設定')
    github_parser.add_argument('--token', help='GitHubパーソナルアクセストークン')
    github_parser.add_argument('--repo', help='リポジトリ名（形式: owner/repo）')

    # GitLabシークレットを設定
    gitlab_parser = subparsers.add_parser('gitlab', help='GitLab CIのシークレットを設定')
    gitlab_parser.add_argument('--token', help='GitLabパーソナルアクセストークン')
    gitlab_parser.add_argument('--project-id', help='GitLabプロジェクトID')

    # キーストアを生成
    keystore_parser = subparsers.add_parser('generate-keystore', help='Androidキーストアを生成')
    keystore_parser.add_argument('--keystore-path', default='keystore.jks', help='出力キーストアパス')

    # キーストアを暗号化
    encrypt_parser = subparsers.add_parser('encrypt-keystore', help='キーストアをBase64エンコード')
    encrypt_parser.add_argument('--keystore-path', default='keystore.jks', help='キーストアパス')

    # プロビジョニングプロファイルを暗号化
    profile_parser = subparsers.add_parser('encrypt-profile', help='iOSプロビジョニングプロファイルをBase64エンコード')
    profile_parser.add_argument('--profile-path', required=True, help='プロビジョニングプロファイルパス')

    # 環境ファイルを生成
    env_parser = subparsers.add_parser('generate-env', help='環境設定ファイルを生成')
    env_parser.add_argument('--env', choices=['dev', 'test', 'prod'], default='dev', help='環境')
    env_parser.add_argument('--output', default='.env', help='出力ファイルパス')

    return parser.parse_args()

def run_command(command):
    """コマンドを実行し、結果を返す"""
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def set_github_secrets(token, repo):
    """GitHub Actionsのシークレットを設定"""
    if not token:
        token = getpass("GitHubパーソナルアクセストークンを入力: ")

    if not repo:
        repo = input("リポジトリ名を入力（形式: owner/repo）: ")

    # シークレット名と値のペアを収集
    secrets = {}
    print("\nGitHub Actionsのシークレットを設定します。")
    print("各シークレットの値を入力してください。空白で終了します。")

    while True:
        name = input("\nシークレット名（空白で終了）: ")
        if not name:
            break

        value = getpass(f"{name}の値: ")
        secrets[name] = value

    # シークレットを設定
    for name, value in secrets.items():
        # GitHub APIを使用してシークレットを設定
        command = f"""
        curl -X PUT \
          -H "Authorization: token {token}" \
          -H "Accept: application/vnd.github.v3+json" \
          https://api.github.com/repos/{repo}/actions/secrets/{name} \
          -d '{{
            "encrypted_value": "{base64.b64encode(value.encode()).decode()}",
            "key_id": "012345678901234567"
          }}'
        """

        result = run_command(command)
        if result.returncode == 0:
            print(f"シークレット {name} を設定しました。")
        else:
            print(f"エラー: シークレット {name} の設定に失敗しました。")
            print(result.stderr)

    print("\n完了しました。")

def set_gitlab_secrets(token, project_id):
    """GitLab CIのシークレットを設定"""
    if not token:
        token = getpass("GitLabパーソナルアクセストークンを入力: ")

    if not project_id:
        project_id = input("GitLabプロジェクトIDを入力: ")

    # シークレット名と値のペアを収集
    variables = {}
    print("\nGitLab CIの変数を設定します。")
    print("各変数の値を入力してください。空白で終了します。")

    while True:
        name = input("\n変数名（空白で終了）: ")
        if not name:
            break

        value = getpass(f"{name}の値: ")
        is_protected = input(f"{name}を保護変数にしますか？（y/n）: ").lower() == 'y'
        is_masked = input(f"{name}をマスク変数にしますか？（y/n）: ").lower() == 'y'

        variables[name] = {
            "value": value,
            "protected": is_protected,
            "masked": is_masked
        }

    # 変数を設定
    for name, config in variables.items():
        # GitLab APIを使用して変数を設定
        command = f"""
        curl -X POST \
          -H "PRIVATE-TOKEN: {token}" \
          "https://gitlab.com/api/v4/projects/{project_id}/variables" \
          -d "key={name}" \
          -d "value={config['value']}" \
          -d "protected={str(config['protected']).lower()}" \
          -d "masked={str(config['masked']).lower()}"
        """

        result = run_command(command)
        if result.returncode == 0:
            print(f"変数 {name} を設定しました。")
        else:
            print(f"エラー: 変数 {name} の設定に失敗しました。")
            print(result.stderr)

    print("\n完了しました。")

def generate_keystore(keystore_path):
    """Androidキーストアを生成"""
    print("Androidキーストアを生成します。")

    alias = input("キーエイリアス名: ")
    keystore_password = getpass("キーストアパスワード: ")
    key_password = getpass("キーパスワード（キーストアパスワードと同じ場合は空白）: ")

    if not key_password:
        key_password = keystore_password

    common_name = input("氏名（CN）: ")
    org_unit = input("組織単位（OU）: ")
    org = input("組織名（O）: ")
    locality = input("市区町村（L）: ")
    state = input("都道府県（ST）: ")
    country = input("国コード（C、例: JP）: ")

    # キーストア生成コマンド
    command = f"""
    keytool -genkey -v \
      -keystore {keystore_path} \
      -alias {alias} \
      -keyalg RSA -keysize 2048 -validity 10000 \
      -storepass {keystore_password} \
      -keypass {key_password} \
      -dname "CN={common_name}, OU={org_unit}, O={org}, L={locality}, ST={state}, C={country}"
    """

    result = run_command(command)
    if result.returncode == 0:
        print(f"キーストアを生成しました: {keystore_path}")

        # キーストア情報を表示
        keystore_info = {
            "keystore_path": keystore_path,
            "alias": alias,
            "keystore_password": keystore_password,
            "key_password": key_password
        }

        print("\nキーストア情報:")
        for key, value in keystore_info.items():
            print(f"  {key}: {value}")

        # CI/CD用の値を出力
        print("\nCI/CD環境変数の設定例:")
        print(f"SIGNING_KEY_ALIAS={alias}")
        print(f"KEY_STORE_PASSWORD={keystore_password}")
        print(f"KEY_PASSWORD={key_password}")

        return True
    else:
        print(f"エラー: キーストア生成に失敗しました。")
        print(result.stderr)
        return False

def encrypt_keystore(keystore_path):
    """キーストアをBase64エンコード"""
    if not os.path.exists(keystore_path):
        print(f"エラー: キーストアファイル {keystore_path} が見つかりません")
        return False

    # ファイルをBase64エンコード
    try:
        with open(keystore_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')

        # 結果を表示（セキュリティのため一部のみ）
        print(f"キーストア {keystore_path} をBase64エンコードしました。")
        print(f"エンコード結果（最初の10文字）: {encoded[:10]}...")

        # 結果をファイルに保存するか確認
        save = input("エンコード結果をファイルに保存しますか？（y/n）: ").lower() == 'y'
        if save:
            output_path = input("出力ファイルパス（デフォルト: keystore_base64.txt）: ") or "keystore_base64.txt"
            with open(output_path, 'w') as f:
                f.write(encoded)
            print(f"エンコード結果を {output_path} に保存しました。")

        # CI/CD用の環境変数名を表示
        print("\nCI/CD環境変数の設定例:")
        print(f"SIGNING_KEY_BASE64=（上記のBase64エンコード文字列）")

        return True
    except Exception as e:
        print(f"エラー: キーストアのエンコードに失敗しました: {e}")
        return False

def encrypt_profile(profile_path):
    """iOSプロビジョニングプロファイルをBase64エンコード"""
    if not os.path.exists(profile_path):
        print(f"エラー: プロビジョニングプロファイル {profile_path} が見つかりません")
        return False

    # ファイルをBase64エンコード
    try:
        with open(profile_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')

        # 結果を表示（セキュリティのため一部のみ）
        print(f"プロファイル {profile_path} をBase64エンコードしました。")
        print(f"エンコード結果（最初の10文字）: {encoded[:10]}...")

        # 結果をファイルに保存するか確認
        save = input("エンコード結果をファイルに保存しますか？（y/n）: ").lower() == 'y'
        if save:
            output_path = input("出力ファイルパス（デフォルト: profile_base64.txt）: ") or "profile_base64.txt"
            with open(output_path, 'w') as f:
                f.write(encoded)
            print(f"エンコード結果を {output_path} に保存しました。")

        # CI/CD用の環境変数名を表示
        print("\nCI/CD環境変数の設定例:")
        print(f"PROVISIONING_PROFILE=（上記のBase64エンコード文字列）")

        return True
    except Exception as e:
        print(f"エラー: プロファイルのエンコードに失敗しました: {e}")
        return False

def generate_env_file(env, output):
    """環境設定ファイルを生成"""
    print(f"{env}環境用の設定ファイルを生成します。")

    # 環境ごとの設定テンプレート
    if env == 'dev':
        template = {
            "API_URL": "https://api-dev.example.com",
            "DEBUG": "true",
            "LOG_LEVEL": "debug"
        }
    elif env == 'test':
        template = {
            "API_URL": "https://api-test.example.com",
            "DEBUG": "true",
            "LOG_LEVEL": "info"
        }
    else:  # prod
        template = {
            "API_URL": "https://api.example.com",
            "DEBUG": "false",
            "LOG_LEVEL": "warning"
        }

    # 各設定値を確認または編集
    settings = {}
    print("\n各設定値を確認または編集してください：")
    for key, default_value in template.items():
        value = input(f"{key} （デフォルト: {default_value}）: ") or default_value
        settings[key] = value

    # 追加の設定があれば入力
    print("\n追加の設定があれば入力してください。キー名が空白で終了します。")
    while True:
        key = input("\n設定キー名（空白で終了）: ")
        if not key:
            break

        value = input(f"{key}の値: ")
        settings[key] = value

    # ファイルに書き込み
    with open(output, 'w') as f:
        for key, value in settings.items():
            f.write(f"{key}={value}\n")

    print(f"\n環境設定ファイルを {output} に保存しました。")
    return True

def main():
    """メイン関数"""
    args = parse_args()

    if args.command == 'github':
        return set_github_secrets(args.token, args.repo)

    elif args.command == 'gitlab':
        return set_gitlab_secrets(args.token, args.project_id)

    elif args.command == 'generate-keystore':
        return generate_keystore(args.keystore_path)

    elif args.command == 'encrypt-keystore':
        return encrypt_keystore(args.keystore_path)

    elif args.command == 'encrypt-profile':
        return encrypt_profile(args.profile_path)

    elif args.command == 'generate-env':
        return generate_env_file(args.env, args.output)

    else:
        print("コマンドを指定してください。ヘルプを表示するには -h を使用してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## CI/CD実装例

実際のプロジェクトで使用できるCI/CD実装の例を示します。以下は、GitHubリポジトリとGitHub Actionsを使用した小規模～中規模のFletアプリケーション向けのワークフロー例です。

### プロジェクト構造

```
flet-app/
├── .github/
│   └── workflows/
│       ├── ci.yml          # 継続的インテグレーション
│       ├── cd-web.yml      # Webアプリのデプロイ
│       ├── cd-android.yml  # Androidアプリのデプロイ
│       └── cd-ios.yml      # iOSアプリのデプロイ
├── app/                    # アプリケーションコード
├── tests/                  # テストコード
├── scripts/                # 自動化スクリプト
│   ├── build_all.py        # マルチプラットフォームビルドスクリプト
│   ├── check_code_quality.py # コード品質チェックスクリプト
│   ├── run_tests.py        # テスト自動化スクリプト
│   ├── setup_git_hooks.py  # Gitフック設定スクリプト
│   ├── setup_secrets.py    # シークレット管理スクリプト
│   └── version_manager.py  # バージョン管理スクリプト
├── docs/                   # ドキュメント
├── distribution/           # 配布関連ファイル
│   ├── screenshots/        # スクリーンショット
│   └── whatsnew/           # リリースノート
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
├── requirements.txt        # 依存関係
└── requirements-dev.txt    # 開発用依存関係
```

### 開発ワークフロー

1. 開発者が機能ブランチ（feature/XXX）またはバグ修正ブランチ（fix/XXX）を作成
2. コードを変更してコミット
3. プルリクエストを作成してdevelopブランチへのマージを要求
4. CI（GitHub Actions）が自動的に実行され、コード品質チェックとテストを実施
5. レビュー後、developブランチにマージ
6. 定期的に（またはリリース前に）developブランチからrelease/vX.Y.Zブランチを作成
7. リリース準備が整ったら、バージョン番号を更新してタグを作成
8. タグがプッシュされると、CDワークフローが自動的に実行されて各プラットフォームへのデプロイを実施

### リリースプロセス

1. `python scripts/version_manager.py bump minor` でバージョンを更新
2. `python scripts/version_manager.py changelog` でチェンジログを更新
3. `python scripts/build_all.py --version X.Y.Z --build-number N --platforms web,android,ios --release` でリリースビルドを実行
4. 各ビルドを手動でテスト
5. `python scripts/version_manager.py release` でリリースを作成（タグ付けとプッシュ）
6. GitHub Actionsが自動的にデプロイワークフローを実行

この実装例は、小規模から中規模のプロジェクトに適しています。より大規模なプロジェクトや複雑な要件がある場合は、必要に応じてカスタマイズしてください。
