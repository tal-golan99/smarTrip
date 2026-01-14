'use client';

import { X, Calendar } from 'lucide-react';

interface RegistrationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function RegistrationModal({ isOpen, onClose }: RegistrationModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative bg-white rounded-2xl shadow-2xl p-8 max-w-md mx-4 text-center transform animate-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 left-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
        
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[#12acbe]/10 flex items-center justify-center">
          <Calendar className="w-8 h-8 text-[#12acbe]" />
        </div>
        
        <h3 className="text-2xl font-bold text-[#076839] mb-4">
          שים לב
        </h3>
        <p className="text-lg text-[#5a5a5a] mb-8">
          פעולה זו עדיין אינה פעילה
        </p>
        
        <button
          onClick={onClose}
          className="px-8 py-3 bg-[#076839] text-white rounded-xl font-bold text-lg hover:bg-[#0ba55c] transition-all shadow-lg"
        >
          חזור
        </button>
      </div>
    </div>
  );
}
