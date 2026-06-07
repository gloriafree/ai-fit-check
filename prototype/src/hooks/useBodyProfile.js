import { useState, useCallback, useMemo } from 'react';
import { loadProfile, saveProfile } from '../lib/storage';
import { DEFAULT_PROFILE } from '../constants/measurements';

export function useBodyProfile() {
  const [profile, setProfile] = useState(() => loadProfile() || { ...DEFAULT_PROFILE });

  const updateProfile = useCallback((updates) => {
    setProfile((prev) => {
      const next = { ...prev, ...updates };
      saveProfile(next);
      return next;
    });
  }, []);

  const hasProfile = useMemo(() => {
    return profile.chest > 0 && profile.waist > 0 && profile.hip > 0;
  }, [profile]);

  return { profile, updateProfile, hasProfile };
}
