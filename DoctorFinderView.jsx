import React, { useState, useEffect, useCallback } from 'react';
import { apiClient } from './api';
import {
  Stethoscope, ArrowLeft, MapPin, Phone, Star, ShieldCheck,
  ExternalLink, Navigation, Search, Compass, Building2,
  RefreshCw, AlertCircle, CheckCircle2, X
} from 'lucide-react';

const SPECIALIZATIONS = [
  { code: 'all', label: 'All Specialties' },
  { code: 'dietitian', label: 'Dietitian & Nutritionist' },
  { code: 'general_physician', label: 'General Physician' },
  { code: 'dermatologist', label: 'Dermatologist' },
  { code: 'gastroenterologist', label: 'Gastroenterologist' },
  { code: 'endocrinologist', label: 'Endocrinologist' },
];

const CITY_CHIPS = ['Hyderabad', 'Bengaluru', 'Chennai', 'Mumbai', 'Delhi', 'Vijayawada'];

export const DoctorFinderView = ({ onBack, onAskGenie }) => {
  const [selectedSpecialty, setSelectedSpecialty] = useState('all');
  const [searchCity, setSearchCity] = useState('Hyderabad');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchDistance, setSearchDistance] = useState(25);

  const [showLocationPrompt, setShowLocationPrompt] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsError, setGpsError] = useState(null);

  const [doctorsList, setDoctorsList] = useState([]);
  const [searchCenterInfo, setSearchCenterInfo] = useState('Hyderabad');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const performSearch = useCallback(async (coordsOverride = undefined, cityOverride = undefined, specOverride = undefined, distOverride = undefined) => {
    setLoading(true);
    setError(null);
    const coords = coordsOverride !== undefined ? coordsOverride : userLocation;
    const city = cityOverride !== undefined ? cityOverride : searchCity;
    const spec = specOverride !== undefined ? specOverride : selectedSpecialty;
    const dist = distOverride !== undefined ? distOverride : searchDistance;

    try {
      const payload = {
        city: city || 'Hyderabad',
        specialization_code: spec !== 'all' ? spec : null,
        query: searchQuery.trim() || null,
        max_distance_km: Number(dist),
        language: 'en',
      };
      if (coords?.lat && coords?.lon) {
        payload.latitude = coords.lat;
        payload.longitude = coords.lon;
      }
      const data = await apiClient.getNearbyDoctors(payload);
      setDoctorsList(data?.doctors || []);
      setSearchCenterInfo(data?.search_center || city);
    } catch (err) {
      setError(err.message || 'Could not fetch nearby doctors right now. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [userLocation, searchCity, selectedSpecialty, searchQuery, searchDistance]);

  useEffect(() => {
    performSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSpecialty, searchDistance]);

  const handleConfirmLocationAccess = () => {
    setShowLocationPrompt(false);
    if (!navigator.geolocation) {
      setGpsError('Geolocation is not supported by your browser. Please search by city instead.');
      return;
    }
    setGpsLoading(true);
    setGpsError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        setUserLocation(loc);
        setGpsLoading(false);
        performSearch(loc, searchCity, selectedSpecialty, searchDistance);
      },
      (err) => {
        setGpsLoading(false);
        setGpsError(
          err.code === err.PERMISSION_DENIED
            ? 'Location permission was declined. You can search by entering a city below.'
            : 'Unable to determine your GPS location. Please search by city instead.'
        );
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setUserLocation(null);
    performSearch(null, searchCity, selectedSpecialty, searchDistance);
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-royal/70 hover:text-royal mb-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Home</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-royal text-lime-electric flex items-center justify-center">
              <Stethoscope className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-royal">
                Nearby Doctors &amp; Dietitians
              </h1>
              <p className="text-xs sm:text-sm text-royal/70">
                Verified clinical practitioners and OpenStreetMap clinic locations
              </p>
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={() => {
            if (userLocation) {
              setUserLocation(null);
              performSearch(null, searchCity, selectedSpecialty, searchDistance);
            } else {
              setShowLocationPrompt(true);
            }
          }}
          disabled={gpsLoading}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 border transition-colors ${
            userLocation
              ? 'bg-lime-electric/35 text-royal-deep border-lime-electric'
              : 'bg-royal hover:bg-royal-light text-white border-royal'
          }`}
        >
          {gpsLoading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-lime-electric" />
              <span>Locating...</span>
            </>
          ) : userLocation ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-lime-dark" />
              <span>Using Your Location (Reset)</span>
            </>
          ) : (
            <>
              <Navigation className="w-4 h-4 text-lime-electric" />
              <span>Use My Location</span>
            </>
          )}
        </button>
      </div>

      {/* Explicit Location Permission Consent Banner */}
      {showLocationPrompt && (
        <div className="fg-card p-5 border-royal/40 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <h2 className="font-bold text-sm text-royal flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-royal" />
              <span>Location Access Permission</span>
            </h2>
            <p className="text-xs text-royal/75">
              May FoodGenie access your device&apos;s location to calculate distances to nearby clinics and doctors?
            </p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              type="button"
              onClick={() => setShowLocationPrompt(false)}
              className="px-3.5 py-2 rounded-xl bg-lavender-mist text-royal text-xs font-bold border border-lavender-border"
            >
              Use City Search
            </button>
            <button
              type="button"
              onClick={handleConfirmLocationAccess}
              className="px-4 py-2 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold"
            >
              Allow Location
            </button>
          </div>
        </div>
      )}

      {gpsError && (
        <div className="px-4 py-2.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>{gpsError}</span>
        </div>
      )}

      {error && (
        <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center justify-between gap-3">
          <span className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </span>
          <button
            type="button"
            onClick={() => performSearch()}
            className="px-3 py-1 rounded-lg bg-red-600 text-white font-bold"
          >
            Retry
          </button>
        </div>
      )}

      {/* Search & Filters */}
      <div className="fg-card p-5 space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="relative md:w-1/3">
            <MapPin className="w-4 h-4 text-royal/45 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchCity}
              onChange={(e) => setSearchCity(e.target.value)}
              placeholder="City (e.g. Hyderabad, Bengaluru)"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
            />
          </div>

          <div className="relative flex-1">
            <Search className="w-4 h-4 text-royal/45 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search doctor name, clinic, or specialty..."
              className="w-full pl-10 pr-8 py-2.5 rounded-xl bg-lavender-light border border-lavender-border text-sm text-royal focus:outline-none focus:border-royal"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-royal/45 hover:text-royal"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="flex items-center gap-1.5">
            {[10, 25, 50].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setSearchDistance(d)}
                className={`px-3 py-2 rounded-xl text-xs font-bold border ${
                  searchDistance === d
                    ? 'bg-royal text-white border-royal'
                    : 'bg-lavender-light text-royal border-lavender-border'
                }`}
              >
                {d} km
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold flex items-center justify-center gap-1.5 disabled:opacity-60"
          >
            <Search className="w-3.5 h-3.5 text-lime-electric" />
            <span>Search</span>
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-lavender-mist">
          <span className="text-[11px] font-bold uppercase text-royal/55 mr-1">Cities:</span>
          {CITY_CHIPS.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => {
                setSearchCity(c);
                setUserLocation(null);
                performSearch(null, c, selectedSpecialty, searchDistance);
              }}
              className={`px-3 py-1 rounded-full text-xs font-bold border ${
                searchCity.toLowerCase() === c.toLowerCase()
                  ? 'bg-royal text-white border-royal'
                  : 'bg-lavender-light text-royal/80 border-lavender-border'
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          {SPECIALIZATIONS.map((s) => (
            <button
              key={s.code}
              type="button"
              onClick={() => setSelectedSpecialty(s.code)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-bold border ${
                selectedSpecialty === s.code
                  ? 'bg-royal text-white border-royal'
                  : 'bg-white text-royal/80 border-lavender-border hover:bg-lavender-light'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Results Info */}
      <div className="text-xs font-bold text-royal/75 flex items-center justify-between flex-wrap gap-2">
        <span>
          Showing <strong>{doctorsList.length}</strong> practitioners near <strong>{searchCenterInfo}</strong> (within {searchDistance} km)
        </span>
        <span className="text-royal/55">Directory &amp; OpenStreetMap data</span>
      </div>

      {/* Results List */}
      {loading ? (
        <div className="py-12 flex items-center justify-center text-royal gap-2 text-xs font-bold">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Searching nearby clinics...</span>
        </div>
      ) : doctorsList.length === 0 ? (
        <div className="fg-card p-8 text-center space-y-3">
          <Compass className="w-10 h-10 text-royal/40 mx-auto" />
          <p className="font-bold text-base text-royal">No verified doctors found within {searchDistance} km</p>
          <p className="text-xs text-royal/65 max-w-md mx-auto">
            Try expanding your search radius to 50 km or selecting a major hub city.
          </p>
          <div className="flex justify-center gap-2">
            <button
              type="button"
              onClick={() => setSearchDistance(50)}
              className="px-4 py-2 rounded-xl bg-royal text-white text-xs font-bold"
            >
              Expand to 50 km
            </button>
            <button
              type="button"
              onClick={() => {
                setSelectedSpecialty('all');
                setSearchQuery('');
                setSearchCity('Hyderabad');
                setUserLocation(null);
                performSearch(null, 'Hyderabad', 'all', 25);
              }}
              className="px-4 py-2 rounded-xl bg-lavender-mist text-royal text-xs font-bold border border-lavender-border"
            >
              Reset Filters
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {doctorsList.map((doc) => (
            <div key={doc.id} className="fg-card p-5 flex flex-col justify-between gap-4">
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-display font-bold text-lg text-royal flex items-center gap-1.5">
                      <span>{doc.name}</span>
                      {doc.verified && <ShieldCheck className="w-4 h-4 text-lime-dark flex-shrink-0" />}
                    </h3>
                    <p className="text-xs font-bold text-lime-dark mt-0.5">{doc.specialty}</p>
                    <p className="text-[11px] text-royal/65 mt-0.5">{doc.qualification}</p>
                  </div>
                  <div className="flex items-center gap-1 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full text-xs font-bold text-amber-900">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{doc.rating}</span>
                  </div>
                </div>

                <div className="bg-lavender-light p-3.5 rounded-2xl border border-lavender-border space-y-1.5 text-xs">
                  <p className="font-bold text-royal flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-royal/70 flex-shrink-0" />
                    <span>{doc.clinic_or_hospital}</span>
                  </p>
                  <p className="text-royal/75 flex items-start gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-royal/60 flex-shrink-0 mt-0.5" />
                    <span>
                      {doc.address}
                      {doc.distance_km !== null && doc.distance_km !== undefined && (
                        <strong className="ml-1.5 text-royal">({doc.distance_km} km away)</strong>
                      )}
                    </span>
                  </p>
                  <p className="text-royal/80 font-semibold flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-royal/60 flex-shrink-0" />
                    <span>{doc.contact_phone}</span>
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex gap-2">
                  <a
                    href={doc.directions_url || doc.map_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 py-2 px-3 rounded-xl bg-lavender-mist hover:bg-royal hover:text-white text-royal text-xs font-bold border border-lavender-border flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Navigation className="w-3.5 h-3.5" />
                    <span>Directions</span>
                    <ExternalLink className="w-3 h-3 opacity-70" />
                  </a>
                  {doc.contact_phone && doc.contact_phone.startsWith('+') && (
                    <a
                      href={`tel:${doc.contact_phone}`}
                      className="py-2 px-4 rounded-xl bg-royal hover:bg-royal-light text-white text-xs font-bold flex items-center gap-1.5 transition-colors"
                    >
                      <Phone className="w-3.5 h-3.5 text-lime-electric" />
                      <span>Call</span>
                    </a>
                  )}
                </div>

                {onAskGenie && (
                  <button
                    type="button"
                    onClick={() =>
                      onAskGenie(
                        `Help me prepare nutrition questions to discuss with ${doc.name} (${doc.specialty}) at ${doc.clinic_or_hospital}.`
                      )
                    }
                    className="w-full py-2 px-3 rounded-xl bg-white hover:bg-lavender-light text-royal text-xs font-bold border border-lavender-border"
                  >
                    Prepare Questions with Genie
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DoctorFinderView;
