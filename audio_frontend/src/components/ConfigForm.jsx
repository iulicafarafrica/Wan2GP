import { useState } from 'react';
import { Settings, ChevronDown, ChevronUp, Cpu, Music2, Zap, Sliders } from 'lucide-react';
import { cn } from '../utils/cn';

export function ConfigForm({ config, onChange, className }) {
  const [expandedSections, setExpandedSections] = useState({
    processing: true,
    swiftf0: false,
    svc: false,
    instrumental: false,
    mixing: false,
    quality: false,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const updateConfig = (section, field, value) => {
    onChange({
      ...config,
      [section]: {
        ...config[section],
        [field]: value
      }
    });
  };

  const updateConfigNested = (section, field, nestedField, value) => {
    onChange({
      ...config,
      [section]: {
        ...config[section],
        [field]: {
          ...config[section][field],
          [nestedField]: value
        }
      }
    });
  };

  const loadProfile = (profile) => {
    // Pre-configured profiles for RTX 3070
    const profiles = {
      fast: {
        processing: { ...config.processing, segment_length: 20, max_concurrent_segments: 2 },
        quality: { ...config.quality, sample_rate: 44100, bit_depth: 16 }
      },
      quality: {
        processing: { ...config.processing, segment_length: 30, max_concurrent_segments: 1 },
        quality: { ...config.quality, sample_rate: 48000, bit_depth: 24, output_format: 'flac' }
      },
      balanced: {
        processing: { ...config.processing, segment_length: 30, max_concurrent_segments: 2 },
        quality: { ...config.quality, sample_rate: 48000, bit_depth: 16 }
      }
    };

    onChange(profiles[profile] || config);
  };

  return (
    <div className={cn('card', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Configuration
        </h3>
        
        {/* Profile quick-select */}
        <div className="flex gap-2">
          <button
            onClick={() => loadProfile('fast')}
            className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            Fast
          </button>
          <button
            onClick={() => loadProfile('balanced')}
            className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            Balanced
          </button>
          <button
            onClick={() => loadProfile('quality')}
            className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            Quality
          </button>
        </div>
      </div>

      {/* Processing Section */}
      <ConfigSection
        title="Processing"
        icon={<Cpu className="w-4 h-4" />}
        expanded={expandedSections.processing}
        onToggle={() => toggleSection('processing')}
      >
        <ConfigField
          label="Segment Length (seconds)"
          type="number"
          value={config.processing?.segment_length || 30}
          onChange={(v) => updateConfig('processing', 'segment_length', parseFloat(v))}
          min={5}
          max={120}
        />
        <ConfigField
          label="Max Concurrent Segments"
          type="number"
          value={config.processing?.max_concurrent_segments || 2}
          onChange={(v) => updateConfig('processing', 'max_concurrent_segments', parseInt(v))}
          min={1}
          max={4}
          help="RTX 3070: Recommended 2"
        />
        <ConfigField
          label="Overlap Duration (seconds)"
          type="number"
          value={config.processing?.overlap_duration || 0.5}
          onChange={(v) => updateConfig('processing', 'overlap_duration', parseFloat(v))}
          min={0}
          max={2}
          step={0.1}
        />
      </ConfigSection>

      {/* SwiftF0 Section */}
      <ConfigSection
        title="SwiftF0 (Pitch)"
        icon={<Zap className="w-4 h-4" />}
        expanded={expandedSections.swiftf0}
        onToggle={() => toggleSection('swiftf0')}
      >
        <ConfigField
          label="Enable SwiftF0"
          type="checkbox"
          value={config.swiftf0?.enabled || true}
          onChange={(v) => updateConfig('swiftf0', 'enabled', v)}
        />
        <ConfigField
          label="Pitch Shift (semitones)"
          type="range"
          value={config.swiftf0?.pitch_shift || 0}
          onChange={(v) => updateConfig('swiftf0', 'pitch_shift', parseInt(v))}
          min={-24}
          max={24}
        />
        <ConfigField
          label="Formant Shift"
          type="range"
          value={config.swiftf0?.formant_shift || 1.0}
          onChange={(v) => updateConfig('swiftf0', 'formant_shift', parseFloat(v))}
          min={0.5}
          max={2}
          step={0.1}
        />
      </ConfigSection>

      {/* SVC Section */}
      <ConfigSection
        title="SVC (Voice Conversion)"
        icon={<Music2 className="w-4 h-4" />}
        expanded={expandedSections.svc}
        onToggle={() => toggleSection('svc')}
      >
        <ConfigField
          label="Enable SVC"
          type="checkbox"
          value={config.svc?.enabled || true}
          onChange={(v) => updateConfig('svc', 'enabled', v)}
        />
        <ConfigField
          label="Variant"
          type="select"
          value={config.svc?.variant || 'so-vits-svc'}
          onChange={(v) => updateConfig('svc', 'variant', v)}
          options={['so-vits-svc', 'hq-svc', 'echo']}
        />
        <ConfigField
          label="F0 Method"
          type="select"
          value={config.svc?.f0_method || 'fcpe'}
          onChange={(v) => updateConfig('svc', 'f0_method', v)}
          options={['crepe', 'crepe-tiny', 'mangio-crepe', 'fcpe', 'hybrid']}
        />
        <ConfigField
          label="Noise Scale"
          type="range"
          value={config.svc?.noise_scale || 0.4}
          onChange={(v) => updateConfig('svc', 'noise_scale', parseFloat(v))}
          min={0}
          max={1}
          step={0.1}
        />
      </ConfigSection>

      {/* Instrumental Section */}
      <ConfigSection
        title="Instrumental Generation"
        icon={<Music2 className="w-4 h-4" />}
        expanded={expandedSections.instrumental}
        onToggle={() => toggleSection('instrumental')}
      >
        <ConfigField
          label="Enable Instrumental"
          type="checkbox"
          value={config.instrumental?.enabled || true}
          onChange={(v) => updateConfig('instrumental', 'enabled', v)}
        />
        <ConfigField
          label="Model"
          type="select"
          value={config.instrumental?.model || 'ace-step'}
          onChange={(v) => updateConfig('instrumental', 'model', v)}
          options={['heartmula', 'ace-step']}
        />
        <ConfigField
          label="Split Vocals"
          type="checkbox"
          value={config.instrumental?.split_vocals || true}
          onChange={(v) => updateConfig('instrumental', 'split_vocals', v)}
        />
      </ConfigSection>

      {/* Quality Section */}
      <ConfigSection
        title="Audio Quality"
        icon={<Sliders className="w-4 h-4" />}
        expanded={expandedSections.quality}
        onToggle={() => toggleSection('quality')}
      >
        <ConfigField
          label="Sample Rate"
          type="select"
          value={config.quality?.sample_rate || 48000}
          onChange={(v) => updateConfig('quality', 'sample_rate', parseInt(v))}
          options={[22050, 44100, 48000, 96000]}
        />
        <ConfigField
          label="Bit Depth"
          type="select"
          value={config.quality?.bit_depth || 16}
          onChange={(v) => updateConfig('quality', 'bit_depth', parseInt(v))}
          options={[16, 24, 32]}
        />
        <ConfigField
          label="Output Format"
          type="select"
          value={config.quality?.output_format || 'wav'}
          onChange={(v) => updateConfig('quality', 'output_format', v)}
          options={['wav', 'flac', 'mp3']}
        />
      </ConfigSection>
    </div>
  );
}

function ConfigSection({ title, icon, expanded, onToggle, children }) {
  return (
    <div className="border-b border-gray-700 last:border-b-0">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-700/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-medium">{title}</span>
        </div>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      
      {expanded && (
        <div className="p-4 pt-0 space-y-4">
          {children}
        </div>
      )}
    </div>
  );
}

function ConfigField({ label, type, value, onChange, options, min, max, step = 1, help }) {
  return (
    <div>
      <label className="label">
        {label}
      </label>
      
      {type === 'checkbox' && (
        <input
          type="checkbox"
          checked={value}
          onChange={(e) => onChange(e.target.checked)}
          className="w-5 h-5 accent-primary-600"
        />
      )}
      
      {type === 'number' && (
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          min={min}
          max={max}
          step={step}
          className="input"
        />
      )}
      
      {type === 'range' && (
        <div>
          <input
            type="range"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            min={min}
            max={max}
            step={step}
            className="w-full accent-primary-600"
          />
          <div className="text-sm text-gray-400 mt-1">{value}</div>
        </div>
      )}
      
      {type === 'select' && (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="input"
        >
          {options.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      )}
      
      {help && (
        <p className="text-xs text-gray-500 mt-1">{help}</p>
      )}
    </div>
  );
}
