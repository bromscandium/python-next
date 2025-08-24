export const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

async function handle(res) {
    if (!res.ok) {
        let msg = `HTTP ${res.status}`;
        try {
            const body = await res.json();
            if (body?.detail) msg = Array.isArray(body.detail) ? body.detail.map(d => d.msg || d).join(", ") : body.detail;
        } catch {}
        throw new Error(msg);
    }
    return res.json();
}

export async function listCats() {
    const res = await fetch(`${API_BASE}/cats/`, { cache: "no-store" });
    return handle(res);
}

export async function createCat(payload) {
    const res = await fetch(`${API_BASE}/cats/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return handle(res);
}

export async function updateSalary(id, salary) {
    const res = await fetch(`${API_BASE}/cats/${id}/salary`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ salary: Number(salary) }),
    });
    return handle(res);
}

export async function deleteCat(id) {
    const res = await fetch(`${API_BASE}/cats/${id}`, { method: "DELETE" });
    if (!res.ok) {
        let msg = `HTTP ${res.status}`;
        try { const b = await res.json(); if (b?.detail) msg = b.detail; } catch {}
        throw new Error(msg);
    }
}
