const RETENTION_DAYS = 3;
const MS_PER_DAY = 24 * 60 * 60 * 1000;

const toDate = (value) => {
    if (!value) return null;
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
};

export const getRetentionDaysRemaining = (record, now = Date.now()) => {
    const threshold = Number(record?.storage_threshold ?? 60);
    const riskScore = Number(record?.risk_score ?? 0);

    if (Number.isFinite(threshold) && riskScore >= threshold) {
        return null;
    }

    const expiresAt = toDate(record?.retention_expires_at);
    if (expiresAt) {
        return Math.max(0, Math.floor((expiresAt.getTime() - now) / MS_PER_DAY));
    }

    const createdAt = toDate(record?.timestamp || record?.imported_at || record?.date);
    if (!createdAt) return null;

    const fallbackExpiresAt = new Date(createdAt.getTime() + (RETENTION_DAYS * MS_PER_DAY));
    return Math.max(0, Math.floor((fallbackExpiresAt.getTime() - now) / MS_PER_DAY));
};

export const getRetentionCountdownLabel = (record, now = Date.now()) => {
    const remainingDays = getRetentionDaysRemaining(record, now);
    if (remainingDays === null) return 'Saved forever';
    return `Will be deleted in ${remainingDays} day${remainingDays === 1 ? '' : 's'}`;
};