"""
AI智能纠正模块 - 使用LLM检查和修正OCR识别错误
"""
import re
from typing import List, Dict, Tuple, Optional


class AICorrector:
    """AI单词纠正器"""
    
    def __init__(self):
        # 常见英语单词列表（基础词库）
        self.common_words = self._load_common_words()
        
    def _load_common_words(self) -> set:
        """加载常见英语单词"""
        words = {
            # 基础词汇
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
            'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
            'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
            'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
            'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
            'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
            'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'was', 'are', 'were', 'been',
            'has', 'had', 'did', 'does', 'doing', 'done', 'having', 'being',
            
            # 常见名词
            'apple', 'banana', 'book', 'computer', 'phone', 'water', 'food',
            'home', 'school', 'student', 'teacher', 'friend', 'family', 'child',
            'children', 'man', 'woman', 'boy', 'girl', 'hand', 'eye', 'head',
            'day', 'night', 'time', 'year', 'week', 'month', 'morning', 'evening',
            'city', 'country', 'world', 'place', 'house', 'room', 'door', 'window',
            'car', 'bus', 'train', 'plane', 'bike', 'walk', 'run', 'jump',
            
            # 常见动词
            'go', 'come', 'get', 'make', 'take', 'see', 'know', 'think', 'say',
            'tell', 'ask', 'answer', 'give', 'find', 'use', 'work', 'call',
            'try', 'need', 'feel', 'become', 'leave', 'put', 'mean', 'keep',
            'let', 'begin', 'seem', 'help', 'show', 'hear', 'play', 'move',
            'live', 'believe', 'bring', 'happen', 'write', 'provide', 'sit',
            'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set',
            
            # 常见形容词
            'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own',
            'other', 'old', 'right', 'big', 'high', 'different', 'small',
            'large', 'next', 'early', 'young', 'important', 'few', 'public',
            'bad', 'same', 'able', 'happy', 'sad', 'beautiful', 'ugly',
            'easy', 'hard', 'difficult', 'simple', 'clean', 'dirty', 'busy',
            'free', 'full', 'empty', 'hot', 'cold', 'warm', 'cool', 'big',
            'small', 'tall', 'short', 'long', 'fast', 'slow', 'early', 'late',
            
            # 常见副词
            'often', 'always', 'usually', 'sometimes', 'never', 'already',
            'just', 'only', 'even', 'back', 'still', 'yet', 'too', 'very',
            'really', 'quite', 'almost', 'enough', 'together', 'instead',
            'however', 'therefore', 'moreover', 'otherwise', 'meanwhile',
            
            # 教材常见词汇
            'beautiful', 'clean', 'hand', 'learn', 'often', 'popular',
            'take', 'time', 'umbrella', 'bring', 'cool', 'soon', 'whose',
            'work', 'silver', 'summer', 'holiday', 'everywhere', 'friendship',
            'hurt', 'judge', 'luck', 'magic', 'mascot', 'necklace', 'olympic',
            'ordinary', 'race', 'ring', 'shell', 'soft', 'toy', 'test', 'trust',
            'watch', 'windy', 'worried', 'wristband', 'answer', 'athlete',
            'collect', 'cyclist', 'email', 'kilometre', 'opera', 'house',
            'quarter', 'special', 'spot', 'stamp', 'train', 'yours',
            'both', 'change', 'come', 'cook', 'cousin', 'doctor', 'driver',
            'family', 'fantastic', 'farmer', 'grandfather', 'grandmother',
            'grandparent', 'granny', 'introduce', 'member', 'nurse', 'police',
            'problem', 'role', 'scene', 'taxi', 'these', 'walk', 'woods', 'word',
            'worker', 'away', 'little', 'riding', 'hood', 'phone', 'run',
        }
        return words
    
    def correct_word(self, word: str, context: str = "") -> Tuple[str, str]:
        """
        纠正单个单词
        
        Args:
            word: 待纠正的单词
            context: 上下文（中文释义）
            
        Returns:
            (纠正后的单词, 纠正说明)
        """
        word_lower = word.lower().strip()
        
        # 如果单词正确，直接返回
        if word_lower in self.common_words:
            return word, "正确"
        
        # 尝试常见拼写错误纠正
        correction = self._common_misspellings(word_lower)
        if correction:
            # 保持原始大小写格式
            if word[0].isupper():
                correction = correction.capitalize()
            return correction, f"纠正: {word} -> {correction}"
        
        # 使用编辑距离找最相似的词
        correction = self._edit_distance_correction(word_lower)
        if correction and correction != word_lower:
            # 保持原始大小写格式
            if word[0].isupper():
                correction = correction.capitalize()
            return correction, f"建议纠正: {word} -> {correction}"
        
        return word, "无法纠正"
    
    def _common_misspellings(self, word: str) -> Optional[str]:
        """常见拼写错误映射"""
        misspellings = {
            # 字母混淆
            'ofien': 'often',
            'ofthen': 'often',
            'offen': 'often',
            'teh': 'the',
            'hte': 'the',
            'adn': 'and',
            'taek': 'take',
            'tkae': 'take',
            'wiht': 'with',
            'hwat': 'what',
            'hwen': 'when',
            'wheer': 'where',
            'wroking': 'working',
            'workign': 'working',
            'gonig': 'going',
            'comign': 'coming',
            'geting': 'getting',
            'runing': 'running',
            'writting': 'writing',
            'stoping': 'stopping',
            'traveling': 'travelling',
            'begining': 'beginning',
            'forgeting': 'forgetting',
            'prefering': 'preferring',
            'occuring': 'occurring',
            'permiting': 'permitting',
            'admiting': 'admitting',
            'submiting': 'submitting',
            'limiting': 'limiting',
            'dieing': 'dying',
            'lieing': 'lying',
            'tieing': 'tying',
            'belive': 'believe',
            'beleive': 'believe',
            'acheive': 'achieve',
            'acheve': 'achieve',
            'freind': 'friend',
            'freindly': 'friendly',
            'beutiful': 'beautiful',
            'beatiful': 'beautiful',
            'beuatiful': 'beautiful',
            'calender': 'calendar',
            'collegue': 'colleague',
            'comming': 'coming',
            'concious': 'conscious',
            'definately': 'definitely',
            'defiantly': 'definitely',
            'definetly': 'definitely',
            'dissapoint': 'disappoint',
            'dissappoint': 'disappoint',
            'embarass': 'embarrass',
            'embaras': 'embarrass',
            'enviroment': 'environment',
            'existance': 'existence',
            'experiance': 'experience',
            'goverment': 'government',
            'govermant': 'government',
            'grammer': 'grammar',
            'harrass': 'harass',
            'harras': 'harass',
            'immediatly': 'immediately',
            'independant': 'independent',
            'independent': 'independent',
            'liason': 'liaison',
            'lonley': 'lonely',
            'loosing': 'losing',
            'looseing': 'losing',
            'maintainance': 'maintenance',
            'maintenence': 'maintenance',
            'millenium': 'millennium',
            'millenium': 'millennium',
            'neccessary': 'necessary',
            'necessary': 'necessary',
            'neccesary': 'necessary',
            'noticable': 'noticeable',
            'occurance': 'occurrence',
            'occurence': 'occurrence',
            'occuring': 'occurring',
            'paralell': 'parallel',
            'parrallel': 'parallel',
            'payed': 'paid',
            'peice': 'piece',
            'persistant': 'persistent',
            'posession': 'possession',
            'possesion': 'possession',
            'prefered': 'preferred',
            'prefering': 'preferring',
            'proffesional': 'professional',
            'profesional': 'professional',
            'publically': 'publicly',
            'recieve': 'receive',
            'recive': 'receive',
            'refering': 'referring',
            'reffering': 'referring',
            'relevent': 'relevant',
            'religous': 'religious',
            'rember': 'remember',
            'remeber': 'remember',
            'resistence': 'resistance',
            'sence': 'sense',
            'seperate': 'separate',
            'seperete': 'separate',
            'sucessful': 'successful',
            'successfull': 'successful',
            'supercede': 'supersede',
            'suprise': 'surprise',
            'surprize': 'surprise',
            'thier': 'their',
            'tommorow': 'tomorrow',
            'tommorrow': 'tomorrow',
            'truely': 'truly',
            'untill': 'until',
            'weild': 'wield',
            'whereever': 'wherever',
            'wierd': 'weird',
            'abscence': 'absence',
            'absense': 'absence',
            'accomodate': 'accommodate',
            'acommodate': 'accommodate',
            'acheive': 'achieve',
            'accross': 'across',
            'adress': 'address',
            'adressing': 'addressing',
            'appearence': 'appearance',
            'arguement': 'argument',
            'assasination': 'assassination',
            'basicly': 'basically',
            'begining': 'beginning',
            'beleive': 'believe',
            'belive': 'believe',
            'bizzare': 'bizarre',
            'buisness': 'business',
            'calender': 'calendar',
            'Carribean': 'Caribbean',
            'catagory': 'category',
            'cemetary': 'cemetery',
            'changable': 'changeable',
            'cheif': 'chief',
            'collaegue': 'colleague',
            'colum': 'column',
            'comming': 'coming',
            'commited': 'committed',
            'comparision': 'comparison',
            'completly': 'completely',
            'concious': 'conscious',
            'contraversy': 'controversy',
            'cooly': 'coolly',
            'daschund': 'dachshund',
            'decieve': 'deceive',
            'definate': 'definite',
            'definately': 'definitely',
            'definatly': 'definitely',
            'desparate': 'desperate',
            'dilema': 'dilemma',
            'dissapoint': 'disappoint',
            'dissapointing': 'disappointing',
            'embarass': 'embarrass',
            'enviroment': 'environment',
            'equiped': 'equipped',
            'exilerate': 'exhilarate',
            'existance': 'existence',
            'experiance': 'experience',
            'extreem': 'extreme',
            'facinate': 'fascinate',
            'Febuary': 'February',
            'firey': 'fiery',
            'flourescent': 'fluorescent',
            'foriegn': 'foreign',
            'freind': 'friend',
            'fullfill': 'fulfill',
            'garantee': 'guarantee',
            'glamourous': 'glamorous',
            'goverment': 'government',
            'grammer': 'grammar',
            'harrass': 'harass',
            'hieght': 'height',
            'humerous': 'humorous',
            'idiosyncracy': 'idiosyncrasy',
            'imediately': 'immediately',
            'immitate': 'imitate',
            'independant': 'independent',
            'indispensible': 'indispensable',
            'innoculate': 'inoculate',
            'inteligence': 'intelligence',
            'jewelery': 'jewelry',
            'kernal': 'kernel',
            'liason': 'liaison',
            'libary': 'library',
            'lightening': 'lightning',
            'lisense': 'license',
            'maintainance': 'maintenance',
            'medeval': 'medieval',
            'memento': 'memento',
            'millenium': 'millennium',
            'miniture': 'miniature',
            'miniscule': 'minuscule',
            'mischievious': 'mischievous',
            'mispell': 'misspell',
            'neccessary': 'necessary',
            'noticable': 'noticeable',
            'occured': 'occurred',
            'occurance': 'occurrence',
            'ocurrence': 'occurrence',
            'paralell': 'parallel',
            'pasttime': 'pastime',
            'pavillion': 'pavilion',
            'peice': 'piece',
            'persistant': 'persistent',
            'personell': 'personnel',
            'plagerize': 'plagiarize',
            'playwrite': 'playwright',
            'posession': 'possession',
            'potatos': 'potatoes',
            'preceeding': 'preceding',
            'presance': 'presence',
            'priviledge': 'privilege',
            'probly': 'probably',
            'promiss': 'promise',
            'pronounciation': 'pronunciation',
            'publically': 'publicly',
            'que': 'queue',
            'questionaire': 'questionnaire',
            'readible': 'readable',
            'realy': 'really',
            'recieve': 'receive',
            'recoginze': 'recognize',
            'recomend': 'recommend',
            'recomendation': 'recommendation',
            'refering': 'referring',
            'referrence': 'reference',
            'relevent': 'relevant',
            'religous': 'religious',
            'repitition': 'repetition',
            'restaraunt': 'restaurant',
            'rhythem': 'rhythm',
            'rythm': 'rhythm',
            'sieze': 'seize',
            'sence': 'sense',
            'seperate': 'separate',
            'sieze': 'seize',
            'sillouette': 'silhouette',
            'similer': 'similar',
            'sincerly': 'sincerely',
            'soverign': 'sovereign',
            'speach': 'speech',
            'stratagy': 'strategy',
            'supercede': 'supersede',
            'suprise': 'surprise',
            'tatoo': 'tattoo',
            'tendancy': 'tendency',
            'therefor': 'therefore',
            'threshhold': 'threshold',
            'tommorrow': 'tomorrow',
            'tounge': 'tongue',
            'truely': 'truly',
            'unfortunatly': 'unfortunately',
            'vaccuum': 'vacuum',
            'vegtable': 'vegetable',
            'vehical': 'vehicle',
            'vilage': 'village',
            'wierd': 'weird',
            'writting': 'writing',
            'yte': 'yet',
            
            # OCR常见错误
            'pofalar': 'popular',
            'poputar': 'popular',
            'takephotos': 'take photos',
            'shwaye': 'show',
            'raco': 'race',
            'tbeuk': 'the uk',
            'bel': 'bell',
            'eany': 'early',
            'holictay': 'holiday',
            'unlt': 'unit',
            'oftien': 'often',
            'ofen': 'often',
            'oftern': 'often',
            'pular': 'popular',
            'brihg': 'bring',
            'brlng': 'bring',
            'slver': 'silver',
            'sof': 'soft',
            'mascpt': 'mascot',
            'mas cot': 'mascot',
            'neklace': 'necklace',
            'wristband': 'wristband',
            'wrist hand': 'wristband',
        }
        return misspellings.get(word)
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _edit_distance_correction(self, word: str) -> Optional[str]:
        """使用编辑距离找最相似的词"""
        if len(word) < 2:
            return None
        
        best_match = None
        best_distance = float('inf')
        
        # 只检查长度相近的词
        for candidate in self.common_words:
            if abs(len(candidate) - len(word)) > 2:
                continue
            
            distance = self._edit_distance(word, candidate)
            
            # 编辑距离<=2且比之前的好
            if distance <= 2 and distance < best_distance:
                best_distance = distance
                best_match = candidate
        
        return best_match
    
    def correct_word_list(self, words: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        纠正单词列表
        
        Args:
            words: 单词列表 [{'english': '...', 'chinese': '...'}, ...]
            
        Returns:
            (纠正后的列表, 修改记录列表)
        """
        corrected = []
        changes = []
        
        for word in words:
            en = word.get('english', '').strip()
            cn = word.get('chinese', '').strip()
            
            # 纠正英文
            corrected_en, note = self.correct_word(en, cn)
            
            corrected_word = {
                'english': corrected_en,
                'chinese': cn,
                'raw_english': en,
                'confidence': word.get('confidence', 1.0)
            }
            
            corrected.append(corrected_word)
            
            # 记录修改
            if corrected_en != en:
                changes.append({
                    'original': en,
                    'corrected': corrected_en,
                    'chinese': cn,
                    'note': note
                })
        
        return corrected, changes


# 全局实例
corrector = AICorrector()


def correct_words(words: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """便捷函数"""
    return corrector.correct_word_list(words)


def correct_spelling(raw_words: List[dict]) -> List[dict]:
    """
    纠正单词拼写（app.py 调用的接口）

    Args:
        raw_words: 原始单词列表 [{'en': '...', 'cn': '...'}, ...]

    Returns:
        纠正后的单词列表 [{'en': '...', 'cn': '...', 'corrected': '...'}, ...]
    """
    # 转换为 AI 纠正器需要的格式
    words_input = []
    for w in raw_words:
        words_input.append({
            'english': w.get('en', ''),
            'chinese': w.get('cn', '')
        })

    corrected, changes = corrector.correct_word_list(words_input)

    # 转换为 app.py 期望的格式
    result = []
    for w in corrected:
        en = w.get('english', '')
        original = w.get('raw_english', en)

        # 检查是否有修改
        corrected_value = w.get('english', '')
        is_corrected = corrected_value != original if original else False

        result.append({
            'en': corrected_value,
            'cn': w.get('chinese', ''),
            'corrected': corrected_value if is_corrected else None
        })

    return result


if __name__ == '__main__':
    # 测试
    test_words = [
        {'english': 'ofien', 'chinese': '经常'},
        {'english': 'beutiful', 'chinese': '美丽的'},
        {'english': 'teh', 'chinese': '这个'},
        {'english': 'apple', 'chinese': '苹果'},
        {'english': 'poputar', 'chinese': '受欢迎的'},
    ]
    
    corrected, changes = correct_words(test_words)
    
    print("纠正结果:")
    for w in corrected:
        print(f"  {w['english']} = {w['chinese']}")
    
    print("\n修改记录:")
    for c in changes:
        print(f"  {c['original']} -> {c['corrected']} ({c['note']})")
