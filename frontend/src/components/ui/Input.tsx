import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'error' | 'success';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', variant = 'default', size = 'md', label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const hasError = !!error;
    const finalVariant = hasError ? 'error' : variant;

    const baseClasses = 'flex w-full rounded-xl border bg-white px-4 py-3 text-sm placeholder:text-secondary-500 focus:outline-none focus:ring-2 transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50';
    
    const variantClasses = {
      default: 'border-secondary-300 focus:border-primary-500 focus:ring-primary-500/20',
      error: 'border-danger-500 focus:border-danger-500 focus:ring-danger-500/20',
      success: 'border-success-500 focus:border-success-500 focus:ring-success-500/20',
    };
    
    const sizeClasses = {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-4 text-sm',
      lg: 'h-12 px-4 text-base',
    };
    
    const inputClasses = `${baseClasses} ${variantClasses[finalVariant]} ${sizeClasses[size]} ${leftIcon ? 'pl-10' : ''} ${rightIcon ? 'pr-10' : ''} ${className}`;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="mb-2 block text-sm font-medium text-secondary-700"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400">
              {leftIcon}
            </div>
          )}
          <input
            id={inputId}
            className={inputClasses}
            ref={ref}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-2 text-sm text-danger-600" role="alert">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-2 text-sm text-secondary-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };