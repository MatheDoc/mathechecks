export default function MonoalphabetischeSubstitutionWidget() {
  const React = require('react');
  const { useState, useMemo } = React;
  const { Card, CardContent } = require('@/components/ui/card');
  const { Button } = require('@/components/ui/button');
  const { Input } = require('@/components/ui/input');

  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

  const plaintexts = [
    'DIE KRYPTOGRAPHIE BESCHAEFTIGT SICH MIT DER VERSCHLUESSELUNG UND ENTSCHLUESSELUNG VON INFORMATIONEN UND SPIELT IN DER MODERNEN KOMMUNIKATION EINE WICHTIGE ROLLE',
    'MONOALPHABETISCHE SUBSTITUTIONEN KOENNEN OFT MIT HILFE EINER HAEUFIGKEITSANALYSE GEKNACKT WERDEN WEIL BESTIMMTE BUCHSTABEN IN DEUTSCHEN TEXTEN BESONDERS OFT AUFTRETEN',
    'EIN LANGERER TEXT ERMOEGLICHT EINE DEUTLICH BESSERE STATISTISCHE ANALYSE DER BUCHSTABENHAEUFIGKEITEN UND HILFT BEIM SYSTEMATISCHEN ENTSCHLUESSELN',
    'DAS VERGLEICHEN DER RELATIVEN HAEUFIGKEITEN VON BUCHSTABEN IST EINE KLASSISCHE METHODE ZUR ANALYSE EINFACHER VERSCHLUESSELUNGSVERFAHREN'
  ];

  function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  function generateSubstitution() {
    const shuffled = shuffleArray(alphabet.split(''));
    const map = {};

    alphabet.split('').forEach((char, index) => {
      map[char] = shuffled[index];
    });

    return map;
  }

  function encrypt(text, substitution) {
    return text
      .split('')
      .map((char) => {
        if (alphabet.includes(char)) {
          return substitution[char];
        }
        return char;
      })
      .join('');
  }

  const [plaintext, setPlaintext] = useState(() => {
    return plaintexts[Math.floor(Math.random() * plaintexts.length)];
  });

  const [substitution, setSubstitution] = useState(generateSubstitution);

  const ciphertext = useMemo(() => {
    return encrypt(plaintext, substitution);
  }, [plaintext, substitution]);

  const [mapping, setMapping] = useState({});

  const germanFrequencies = {
    E: 17.4,
    N: 9.8,
    I: 7.6,
    S: 7.3,
    R: 7.0,
    A: 6.5,
    T: 6.2,
    D: 5.1,
    H: 4.8,
    U: 4.4,
    L: 3.4,
    C: 3.1,
    G: 3.0,
    M: 2.5,
    O: 2.5,
    B: 1.9,
    W: 1.9,
    F: 1.7,
    K: 1.2,
    Z: 1.1,
    P: 0.8,
    V: 0.7,
    J: 0.3,
    Y: 0.04,
    X: 0.03,
    Q: 0.02
  };

  const decodedText = ciphertext
    .split('')
    .map((char) => {
      if (alphabet.includes(char)) {
        return mapping[char] || '_';
      }
      return char;
    })
    .join('');

  function handleMappingChange(cipherChar, value) {
    const upper = value.toUpperCase();

    if (upper === '' || alphabet.includes(upper)) {
      setMapping((prev) => ({
        ...prev,
        [cipherChar]: upper
      }));
    }
  }

  function newChallenge() {
    const nextPlaintext = plaintexts[Math.floor(Math.random() * plaintexts.length)];
    setPlaintext(nextPlaintext);
    setSubstitution(generateSubstitution());
    setMapping({});
  }

  const solved = decodedText === plaintext;

  const uniqueCipherLetters = [...new Set(ciphertext.replace(/[^A-Z]/g, '').split(''))].sort();

  const cipherFrequencies = useMemo(() => {
    const counts = {};
    const letters = ciphertext.replace(/[^A-Z]/g, '').split('');

    letters.forEach((letter) => {
      counts[letter] = (counts[letter] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([letter, count]) => ({
        letter,
        frequency: ((count / letters.length) * 100).toFixed(1)
      }))
      .sort((a, b) => b.frequency - a.frequency);
  }, [ciphertext]);

  const germanFrequencyList = Object.entries(germanFrequencies)
    .map(([letter, frequency]) => ({ letter, frequency }))
    .sort((a, b) => b.frequency - a.frequency);

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex items-center justify-center">
      <Card className="w-full max-w-5xl rounded-3xl shadow-2xl">
        <CardContent className="p-8 space-y-8">
          <div className="space-y-2 text-center">
            <h1 className="text-4xl font-bold">Monoalphabetische Substitution</h1>
            <p className="text-gray-600 text-lg">
              Nutzen Sie die Häufigkeitsanalyse und vergleichen Sie die relativen Häufigkeiten der Buchstaben mit typischen deutschen Texten.
            </p>
          </div>

          <div className="bg-gray-50 rounded-2xl p-6 border">
            <h2 className="text-xl font-semibold mb-4">Verschlüsselter Text</h2>
            <div className="text-2xl font-mono tracking-widest break-words leading-relaxed">
              {ciphertext}
            </div>
          </div>

          <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200">
            <h2 className="text-xl font-semibold mb-4">Ihr Entschlüsselungsversuch</h2>
            <div className="text-2xl font-mono tracking-widest break-words leading-relaxed">
              {decodedText}
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            <div className="bg-white border rounded-2xl p-6">
              <h2 className="text-xl font-semibold mb-4">
                Häufigkeiten im Geheimtext
              </h2>

              <div className="space-y-2">
                {cipherFrequencies.map((item) => (
                  <div
                    key={item.letter}
                    className="flex justify-between font-mono border-b pb-1"
                  >
                    <span>{item.letter}</span>
                    <span>{item.frequency} %</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white border rounded-2xl p-6">
              <h2 className="text-xl font-semibold mb-4">
                Typische Häufigkeiten im Deutschen
              </h2>

              <div className="space-y-2">
                {germanFrequencyList.map((item) => (
                  <div
                    key={item.letter}
                    className="flex justify-between font-mono border-b pb-1"
                  >
                    <span>{item.letter}</span>
                    <span>{item.frequency} %</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-4">Buchstaben-Zuordnung</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {uniqueCipherLetters.map((cipherChar) => (
                <div
                  key={cipherChar}
                  className="bg-white border rounded-2xl p-4 flex flex-col items-center gap-2 shadow-sm"
                >
                  <div className="text-sm text-gray-500">Geheimtext</div>
                  <div className="text-2xl font-bold font-mono">{cipherChar}</div>

                  <div className="text-sm text-gray-500">Klartext</div>

                  <Input
                    maxLength={1}
                    value={mapping[cipherChar] || ''}
                    onChange={(e) => handleMappingChange(cipherChar, e.target.value)}
                    className="text-center text-xl font-mono"
                  />
                </div>
              ))}
            </div>
          </div>

          {solved && (
            <div className="bg-green-100 border border-green-300 rounded-2xl p-6 text-center space-y-2">
              <div className="text-3xl font-bold text-green-700">Erfolgreich entschlüsselt</div>
              <div className="text-lg font-mono">{plaintext}</div>
            </div>
          )}

          <div className="flex justify-center pt-4">
            <Button
              onClick={newChallenge}
              className="rounded-2xl px-8 py-6 text-lg"
            >
              Neue Aufgabe
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
