<?php

namespace App\View\Components;

use Closure;
use Illuminate\Contracts\View\View;
use Illuminate\View\Component;

class ResponsiveNavLink extends Component
{
    /**
     * Create a new component instance.
     */
    public function __construct(
        public bool $active = false,
        public string $href = '#'
    ) {
        //
    }

    /**
     * Get the view / contents that represent the component.
     */
    public function render(): View|Closure|string
    {
        return view('components.responsive-nav-link');
    }
}
