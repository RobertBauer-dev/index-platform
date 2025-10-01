import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className = '', variant = 'default', padding = 'md', header, footer, children, ...props }, ref) => {
    const baseClasses = 'rounded-2xl bg-white shadow-soft border border-secondary-100 transition-all duration-200';
    
    const variantClasses = {
      default: 'bg-white',
      elevated: 'shadow-medium hover:shadow-strong',
      outlined: 'border-secondary-200 shadow-none',
      filled: 'bg-secondary-50 border-secondary-200',
    };
    
    const paddingClasses = {
      none: 'p-0',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
      xl: 'p-10',
    };
    
    const classes = `${baseClasses} ${variantClasses[variant]} ${paddingClasses[padding]} ${className}`;

    return (
      <div
        ref={ref}
        className={classes}
        {...props}
      >
        {header && (
          <div className="border-b border-secondary-100 pb-4 mb-6">
            {header}
          </div>
        )}
        <div className="flex-1">{children}</div>
        {footer && (
          <div className="border-t border-secondary-100 pt-4 mt-6">
            {footer}
          </div>
        )}
      </div>
    );
  }
);

Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className = '', ...props }, ref) => (
  <div
    ref={ref}
    className={`flex flex-col space-y-1.5 ${className}`}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className = '', ...props }, ref) => (
  <h3
    ref={ref}
    className={`text-lg font-semibold leading-none tracking-tight text-secondary-900 ${className}`}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className = '', ...props }, ref) => (
  <p
    ref={ref}
    className={`text-sm text-secondary-600 ${className}`}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className = '', ...props }, ref) => (
  <div ref={ref} className={className} {...props} />
));
CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className = '', ...props }, ref) => (
  <div
    ref={ref}
    className={`flex items-center ${className}`}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };