/**
 * Logout confirmation modal - Asks user to confirm before logging out.
 */
'use client';

interface LogoutConfirmModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function LogoutConfirmModal({ isOpen, onConfirm, onCancel }: LogoutConfirmModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-6 md:p-8 max-w-md w-full mx-4">
        <h3 className="text-xl md:text-2xl font-bold text-gray-800 mb-4 text-center">
          האם ברצונך להתנתק מהמערכת?
        </h3>
        <div className="flex gap-4 justify-center">
          <button
            onClick={onConfirm}
            className="px-6 py-3 bg-[#076839] text-white rounded-lg font-semibold hover:bg-[#065a2e] transition-colors"
            type="button"
          >
            כן
          </button>
          <button
            onClick={onCancel}
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
            type="button"
          >
            לא
          </button>
        </div>
      </div>
    </div>
  );
}
