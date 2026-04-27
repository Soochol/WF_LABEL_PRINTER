#!/bin/bash
# WF Label Printer - 원클릭 배포 스크립트
# 사용법: ./deploy.sh

set -e

REPO="Soochol/WF_LABEL_PRINTER"
ARTIFACT_NAME="WF_Label_Printer"
SMB_PATH="/run/user/1000/gvfs/smb-share:server=server-pc.local,share=server%20e"
DEPLOY_DIR="$SMB_PATH/WF_Label_Printer"
TEMP_DIR="/tmp/wf_deploy"

echo "========================================"
echo "  WF Label Printer - Deploy"
echo "========================================"

# 1. 최신 빌드 확인
echo "[1/4] 최신 빌드 확인..."
RUN_ID=$(gh run list --repo "$REPO" --workflow="Build Windows EXE" --status=completed --json databaseId,conclusion --limit 1 -q '.[0] | select(.conclusion=="success") | .databaseId')

if [ -z "$RUN_ID" ]; then
    echo "ERROR: 성공한 빌드가 없습니다."
    exit 1
fi
echo "  빌드 ID: $RUN_ID"

# 2. 아티팩트 다운로드
echo "[2/4] 아티팩트 다운로드..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
gh run download "$RUN_ID" --repo "$REPO" --name "$ARTIFACT_NAME" --dir "$TEMP_DIR"
echo "  다운로드 완료"

# 3. 배포 PC로 복사
echo "[3/4] 배포 PC로 복사..."
if [ ! -d "$SMB_PATH" ]; then
    echo "ERROR: SMB 공유 폴더에 접근할 수 없습니다: $SMB_PATH"
    exit 1
fi

rm -rf "$DEPLOY_DIR" 2>/dev/null || true
mkdir "$DEPLOY_DIR" 2>/dev/null || true
cp -r "$TEMP_DIR"/* "$DEPLOY_DIR"/
echo "  복사 완료: $DEPLOY_DIR"

# 4. 정리
echo "[4/4] 임시 파일 정리..."
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
echo "  배포 완료!"
echo "  배포 PC에서 실행:"
echo "  Server E > WF_Label_Printer > WF_Label_Printer.exe"
echo "========================================"
