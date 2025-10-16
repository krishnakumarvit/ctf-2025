import React, { useState } from 'react';
import { Sparkles, Lock, Unlock, Terminal, Coffee } from 'lucide-react';

export default function VibeCodingCTF() {
  const [currentLevel, setCurrentLevel] = useState(1);
  const [input, setInput] = useState('');
  const [message, setMessage] = useState('');
  const [unlockedLevels, setUnlockedLevels] = useState([1]);
  const [attempts, setAttempts] = useState(0);

  const levels = {
    1: {
      title: "The Aesthetic Function",
      description: "This function values vibes over efficiency. What does it return?",
      code: `function vibeCheck(mood) {
  const ✨ = mood.length;
  const 🌙 = mood.split('').reverse().join('');
  const 🎨 = ✨ * 🌙.charCodeAt(0);
  
  return 🎨.toString(36);
}

// vibeCheck("CTF")`,
      answer: "2qo",
      hint: "Follow the emojis: length, reverse, calculate, convert to base36"
    },
    2: {
      title: "The Feeling Array",
      description: "This array is sorted by vibes, not numbers. What's the pattern?",
      code: `const vibeArray = [
  { val: 13, energy: "✨✨✨" },
  { val: 7, energy: "✨✨" },
  { val: 42, energy: "✨✨✨✨" },
  { val: 1, energy: "✨" }
];

// The flag is the sum of values 
// where energy matches the value's 
// number of prime factors`,
      answer: "14",
      hint: "Count prime factors: 13(1✨), 7(1✨), 42(3✨: 2,3,7), 1(0✨). Match energy length!"
    },
    3: {
      title: "The Mood Cipher",
      description: "Decode the vibe to find the flag.",
      code: `const moodCipher = (s) => {
  let vibe = "";
  const feels = "happy";
  
  for (let i = 0; i < s.length; i++) {
    const shift = feels.charCodeAt(i % feels.length) - 96;
    const c = s.charCodeAt(i);
    
    if (c >= 97 && c <= 122) {
      vibe += String.fromCharCode(
        ((c - 97 + shift) % 26) + 97
      );
    } else {
      vibe += s[i];
    }
  }
  return vibe;
};

// Encrypted: "hamzx"
// Decrypt it!`,
      answer: "cyber",
      hint: "The cipher uses 'happy' as key. Reverse the shift operation!"
    },
    4: {
      title: "The Final Vibe",
      description: "Combine all previous answers in the ultimate vibe check.",
      code: `function ultimateVibe(a, b, c) {
  const ☯️ = a + b.split('').reverse().join('') + c;
  const 🔮 = ☯️.split('').map(
    (x, i) => x.charCodeAt(0) ^ i
  ).reduce((a, b) => a + b, 0);
  
  return 🔮.toString(16).toUpperCase();
}

// ultimateVibe(level1, level2, level3)
// Format: CTF{RESULT}`,
      answer: "CTF{3A7}",
      hint: "Combine: '2qo' + '41' (reversed) + 'cyber', XOR each char with index, sum, convert to hex"
    }
  };

  const checkAnswer = () => {
    const level = levels[currentLevel];
    setAttempts(attempts + 1);
    
    if (input.trim().toLowerCase() === level.answer.toLowerCase()) {
      setMessage('🎉 Correct! The vibes are immaculate!');
      
      if (currentLevel < 4) {
        setTimeout(() => {
          const nextLevel = currentLevel + 1;
          setUnlockedLevels([...unlockedLevels, nextLevel]);
          setCurrentLevel(nextLevel);
          setInput('');
          setMessage('');
        }, 1500);
      } else {
        setMessage('🏆 Challenge Complete! You are a true vibe coding master!');
      }
    } else {
      setMessage('❌ Not quite... the vibes are off. Try again!');
    }
  };

  const level = levels[currentLevel];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-pink-900 to-indigo-900 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="w-12 h-12 text-yellow-300 animate-pulse" />
            <h1 className="text-5xl font-bold text-white">Vibe Coding CTF</h1>
            <Coffee className="w-12 h-12 text-yellow-300 animate-pulse" />
          </div>
          <p className="text-pink-200 text-lg">
            Where aesthetics meet algorithms ✨
          </p>
          <div className="mt-4 text-purple-200">
            Attempts: {attempts}
          </div>
        </div>

        {/* Level Progress */}
        <div className="flex gap-4 mb-8 justify-center">
          {[1, 2, 3, 4].map(num => (
            <button
              key={num}
              onClick={() => {
                if (unlockedLevels.includes(num)) {
                  setCurrentLevel(num);
                  setInput('');
                  setMessage('');
                }
              }}
              disabled={!unlockedLevels.includes(num)}
              className={`w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold transition-all ${
                unlockedLevels.includes(num)
                  ? currentLevel === num
                    ? 'bg-yellow-400 text-purple-900 scale-110 shadow-lg'
                    : 'bg-purple-600 text-white hover:bg-purple-500'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              {unlockedLevels.includes(num) ? (
                <Unlock className="w-6 h-6" />
              ) : (
                <Lock className="w-6 h-6" />
              )}
            </button>
          ))}
        </div>

        {/* Challenge Card */}
        <div className="bg-black bg-opacity-50 backdrop-blur-lg rounded-lg p-8 shadow-2xl border-2 border-purple-500">
          <div className="flex items-center gap-3 mb-4">
            <Terminal className="w-8 h-8 text-green-400" />
            <h2 className="text-3xl font-bold text-white">
              Level {currentLevel}: {level.title}
            </h2>
          </div>
          
          <p className="text-purple-200 mb-6 text-lg">{level.description}</p>

          {/* Code Display */}
          <div className="bg-gray-900 rounded-lg p-6 mb-6 font-mono text-sm overflow-x-auto border border-green-500">
            <pre className="text-green-300 whitespace-pre-wrap">
              {level.code}
            </pre>
          </div>

          {/* Input Area */}
          <div className="space-y-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && checkAnswer()}
              placeholder="Enter your answer..."
              className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border-2 border-purple-500 focus:border-pink-500 focus:outline-none text-lg"
            />
            
            <button
              onClick={checkAnswer}
              className="w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white py-3 rounded-lg font-bold text-lg hover:from-pink-600 hover:to-purple-700 transition-all shadow-lg"
            >
              Submit Answer
            </button>

            <details className="text-purple-300">
              <summary className="cursor-pointer hover:text-purple-100">
                💡 Need a hint?
              </summary>
              <p className="mt-2 text-sm bg-purple-900 bg-opacity-50 p-3 rounded">
                {level.hint}
              </p>
            </details>
          </div>

          {/* Message Display */}
          {message && (
            <div className={`mt-6 p-4 rounded-lg text-center font-bold text-lg ${
              message.includes('Correct') || message.includes('Complete')
                ? 'bg-green-600 text-white'
                : 'bg-red-600 text-white'
            }`}>
              {message}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-purple-300">
          <p className="text-sm">
            "Code with feeling, debug with intuition" - Ancient Vibe Coder Proverb
          </p>
        </div>
      </div>
    </div>
  );
}