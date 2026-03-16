function createSeededRng(seedInput = "") {
    const seedStr = String(seedInput || "seed");
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i += 1) {
        h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353);
        h = (h << 13) | (h >>> 19);
    }

    return function rng() {
        h = Math.imul(h ^ (h >>> 16), 2246822507);
        h = Math.imul(h ^ (h >>> 13), 3266489909);
        const t = (h ^= h >>> 16) >>> 0;
        return t / 4294967296;
    };
}

export function shuffleQuestionsInTask(task, seed = "") {
    const fragen = Array.isArray(task?.fragen) ? task.fragen : [];
    const antworten = Array.isArray(task?.antworten) ? task.antworten : [];
    const count = Math.min(fragen.length, antworten.length);
    if (count <= 1) return task;

    const rng = createSeededRng(seed);
    const indices = Array.from({ length: count }, (_, i) => i);

    for (let i = count - 1; i > 0; i -= 1) {
        const j = Math.floor(rng() * (i + 1));
        [indices[i], indices[j]] = [indices[j], indices[i]];
    }

    return {
        ...task,
        fragen: indices.map((i) => fragen[i]),
        antworten: indices.map((i) => antworten[i]),
    };
}
