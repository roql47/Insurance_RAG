/**
 * @description 마크다운 텍스트를 일반 텍스트로 변환
 * @param {string} markdown 마크다운 텍스트
 * @returns {string} 일반 텍스트
 * 
 * @author hehee https://github.com/hehee9
 * @license CC BY-NC-SA 4.0
 * - 저작권자 표기
 * - 라이선스 표기
 * - 상업적 이용 금지
 * - 동일 조건 변경 가능
 */
export function mdToText(markdown) {
    const MD_PATTERNS = {
        CODE_BLOCK: /```(.*?)\n([\s\S]*?)```/g,
        INLINE_CODE: /`([^`]+)`/g,
        BOLD_ITALIC: /(\*\*\*|___)(.*?)\1/g,
        BOLD: /(\*\*|__)(.*?)\1/g,
        ITALIC: /(\*|_)(.*?)\1/g,
        STRIKETHROUGH: /~~(.*?)~~/g,
        IMAGE: /(!?)\[([^\]]+)\]\(([^)]+)\)/g,
        HORIZONTAL_LINE: /^([-*]){3,}$/gm,
        HEADING: /^(#+)\s+(.*)/gm,
        LIST: /^([ \t]*)([-*])\s+(.*)/gm,
        BLOCKQUOTE: /^((?:>\s*)+)(.*)/gm
    };

    const codeBlocks = [];
    const inlineCodes = [];
    const protectedUrls = [];
    const URL_REGEX = /(?:https?:\/\/)[^\s\[\]()]*/g;

    // 다른 마크다운 변환에 영향을 안 받도록 특수문자 사용
    const indexChar = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９";
    const TOKEN_START = "乜𪚥";
    const TOKEN_END = "𪚥乜";
    const TOKEN_URL = "有斡恚累";
    const TOKEN_CODE = "高頭不歷";
    const TOKEN_INLINE = "引羅引";


    /** @description 볼드체 특수문자 변환 함수 (숫자, 알파벳) */
    function convertToBoldSpecial(text) {
        return text.replace(/[0-9a-zA-Z]/g, (char) => {
            if (char >= "0" && char <= "9") return String.fromCodePoint(0x1D7CE + (char.charCodeAt(0) - "0".charCodeAt(0)));
            else if (char >= "A" && char <= "Z") return String.fromCodePoint(0x1D5D4 + (char.charCodeAt(0) - "A".charCodeAt(0)));
            else if (char >= "a" && char <= "z") return String.fromCodePoint(0x1D5EE + (char.charCodeAt(0) - "a".charCodeAt(0)));
            return char;
        });
    }

    /** @description 이탤릭체 특수문자 변환 함수 (알파벳) */
    function convertToItalicSpecial(text) {
        return text.replace(/[a-zA-Z]/g, (char) => {
            if (char >= "A" && char <= "Z") return String.fromCodePoint(0x1D608 + (char.charCodeAt(0) - "A".charCodeAt(0)));
            else if (char >= "a" && char <= "z") return String.fromCodePoint(0x1D622 + (char.charCodeAt(0) - "a".charCodeAt(0)));
            return char;
        });
    }

    /** @description 볼드+이탤릭체 특수문자 변환 함수 (알파벳, 숫자) */
    function convertToBoldItalicSpecial(text) {
        return text.replace(/[0-9a-zA-Z]/g, (char) => {
            if (char >= "0" && char <= "9") return String.fromCodePoint(0x1D7CE + (char.charCodeAt(0) - "0".charCodeAt(0)));
            else if (char >= "A" && char <= "Z") return String.fromCodePoint(0x1D63C + (char.charCodeAt(0) - "A".charCodeAt(0)));
            else if (char >= "a" && char <= "z") return String.fromCodePoint(0x1D656 + (char.charCodeAt(0) - "a".charCodeAt(0)));
            return char;
        });
    }

    /** @description 텍스트가 모두 변환 가능한 문자인지 확인 */
    function isAllConvertible(text, includeNumbers) {
        // 허용 특수문자
        const allowedSpecialChars = [
            "+", "-", "*", "/", "=", "<", ">", "%", "^", "±", "×", "÷", "°",
            "!", "?", ".", ",", ":", ";", "'", '"', "`",
            "(", ")", "[", "]", "{", "}",
            "@", "#", "$", "&", "|", "\\", "_", "~", "§", "©", "®", "™", "€", "£", "¥", "¢",
            
            "！", "？", "．", "，", "：", "；", "＇", "＂",
            "（", "）", "［", "］", "｛", "｝", "〈", "〉", "《", "》", "「", "」", "『", "』",
            "＠", "＃", "＄", "％", "＆", "＊", "＋", "－", "＝", "＼", "｜", "～", "＿",
            "※", "★", "☆", "♪", "♡", "♢", "♦", "♧", "♠"
        ];
        
        // 정규식에서 사용할 수 있도록 이스케이프
        const escapedChars = allowedSpecialChars.map(char => 
            char.replace(/[.*+?^${}()|[\]\\-]/g, '\\$&')
        ).join('');
        
        // 숫자 포함 여부에 따라 패턴 결정
        const numberPattern = includeNumbers ? '0-9' : '';
        const allowedPattern = new RegExp(`^[${numberPattern}a-zA-Z\\s${escapedChars}]*$`);
        return allowedPattern.test(text);
    }


    /** @description 볼드체 처리 함수 */
    function processBold(match, delimiter, content) {
        const converted = convertToBoldSpecial(content);
        return isAllConvertible(content, true) ? converted : "❪" + converted + "❫";
    }

    /** @description 이탤릭체 처리 함수 */
    function processItalic(match, delimiter, content) {
        const converted = convertToItalicSpecial(content);
        return isAllConvertible(content, false) ? converted : "❬" + converted + "❭";
    }

    /** @description 볼드+이탤릭체 처리 함수 */
    function processBoldItalic(match, delimiter, content) {
        const converted = convertToBoldItalicSpecial(content);
        return isAllConvertible(content, true) ? converted : "❮" + converted + "❯";
    }

    // 입력값 검증
    if (!markdown || typeof markdown !== 'string') return '';

    let result = markdown;

    // 1. URL 보호
    result = result.replace(URL_REGEX, (url) => {
        protectedUrls.push(url);
        return TOKEN_URL + indexChar[protectedUrls.length - 1];
    });

    // 2. 코드 블록 보호
    result = result.replace(MD_PATTERNS.CODE_BLOCK, (match, lang, code) => {
        codeBlocks.push(code.trim());
        return TOKEN_CODE + indexChar[codeBlocks.length - 1];
    });

    // 3. 인라인 코드 보호
    result = result.replace(MD_PATTERNS.INLINE_CODE, (match, code) => {
        inlineCodes.push(code);
        return TOKEN_INLINE + indexChar[inlineCodes.length - 1];
    });

    // 4. 볼드+이탤릭 처리 (먼저 처리해야 함)
    result = result.replace(MD_PATTERNS.BOLD_ITALIC, processBoldItalic);

    // 5. 볼드 처리
    result = result.replace(MD_PATTERNS.BOLD, processBold);

    // 6. 이탤릭 처리
    result = result.replace(MD_PATTERNS.ITALIC, processItalic);

    // 7. 취소선 처리
    result = result.replace(MD_PATTERNS.STRIKETHROUGH, (match, content) => "̶" + content + "̶");

    // 8. 이미지 처리
    result = result.replace(MD_PATTERNS.IMAGE, (match, isImage, altText, url) => {
        return isImage ? `[이미지: ${altText}]` : altText;
    });

    // 9. 수평선 제거
    result = result.replace(MD_PATTERNS.HORIZONTAL_LINE, "─".repeat(30));

    // 10. 헤딩 처리
    result = result.replace(MD_PATTERNS.HEADING, (match, hashes, content) => {
        const level = hashes.length;
        return "\n" + "═".repeat(Math.max(1, 7 - level)) + " " + content + " " + "═".repeat(Math.max(1, 7 - level)) + "\n";
    });

    // 11. 리스트 처리
    result = result.replace(MD_PATTERNS.LIST, (match, indent, marker, content) => {
        const indentLevel = Math.floor(indent.length / 2);
        return "  ".repeat(indentLevel) + "• " + content;
    });

    // 12. 인용구 처리
    result = result.replace(MD_PATTERNS.BLOCKQUOTE, (match, markers, content) => {
        const level = markers.trim().split('>').length - 1;
        return "│ ".repeat(level) + content;
    });

    // 13. 보호된 요소 복원 (역순)
    result = result.replace(new RegExp(TOKEN_INLINE + `([${indexChar}])`, 'g'), (match, index) => {
        const idx = indexChar.indexOf(index);
        return TOKEN_START + inlineCodes[idx] + TOKEN_END;
    });

    result = result.replace(new RegExp(TOKEN_CODE + `([${indexChar}])`, 'g'), (match, index) => {
        const idx = indexChar.indexOf(index);
        return "\n" + TOKEN_START + codeBlocks[idx] + TOKEN_END + "\n";
    });

    result = result.replace(new RegExp(TOKEN_URL + `([${indexChar}])`, 'g'), (match, index) => {
        const idx = indexChar.indexOf(index);
        return protectedUrls[idx];
    });

    // 14. 연속된 빈 줄 정리
    result = result.replace(/\n{3,}/g, '\n\n');

    return result.trim();
}

