@extends('layouts.admin')

@section('title', 'Viết lại bài viết bằng AI')

@section('content')
<div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto bg-white shadow-md rounded-lg p-6">
        <div class="mb-6">
            <h1 class="text-2xl font-bold text-gray-900">Viết lại bài viết bằng AI</h1>
            <p class="mt-1 text-sm text-gray-500">Sử dụng AI để viết lại bài viết hiện tại.</p>
        </div>

        @if(session('error'))
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                <span class="block sm:inline">{{ session('error') }}</span>
            </div>
        @endif

        <form action="{{ route('admin.rewritten-articles.ai-rewrite', $rewrittenArticle) }}" method="POST" class="space-y-8" enctype="multipart/form-data">
            @csrf
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Thông tin bài viết</h3>
                
                <div class="grid grid-cols-1 gap-y-4">
                    <div>
                        <p class="block text-sm font-medium text-gray-700 mb-1">
                            Tiêu đề bài viết
                        </p>
                        <p class="text-base text-gray-900">{{ $rewrittenArticle->title }}</p>
                    </div>

                    <div>
                        <p class="block text-sm font-medium text-gray-700 mb-1">
                            Trạng thái hiện tại
                        </p>
                        <p class="inline-flex px-2 py-1 rounded-full text-xs font-medium {{ $rewrittenArticle->status_badge_class }}">
                            {{ ucfirst($rewrittenArticle->status) }}
                        </p>
                    </div>

                    <div>
                        <label for="category_id" class="block text-sm font-medium text-gray-700">
                            Danh mục
                        </label>
                        <div class="mt-1">
                            <select id="category_id" name="category_id" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" required>
                                <option value="" disabled>-- Chọn danh mục --</option>
                                @foreach($categories as $category)
                                    <option value="{{ $category->id }}" {{ $rewrittenArticle->category_id == $category->id ? 'selected' : '' }}>
                                        {{ $category->name }}
                                    </option>
                                @endforeach
                            </select>
                            @error('category_id')
                                <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                            @enderror
                        </div>
                    </div>

                    <div>
                        <label for="subcategory_id" class="block text-sm font-medium text-gray-700">
                            Danh mục con
                        </label>
                        <div class="mt-1">
                            <select id="subcategory_id" name="subcategory_id" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                                <option value="">-- Chọn danh mục con --</option>
                                @if($rewrittenArticle->category && $rewrittenArticle->category->subcategories)
                                    @foreach($rewrittenArticle->category->subcategories as $subcategory)
                                        <option value="{{ $subcategory->id }}" {{ $rewrittenArticle->subcategory_id == $subcategory->id ? 'selected' : '' }}>
                                            {{ $subcategory->name }}
                                        </option>
                                    @endforeach
                                @endif
                            </select>
                            @error('subcategory_id')
                                <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                            @enderror
                        </div>
                    </div>
                    
                    @if($rewrittenArticle->originalArticle && ($rewrittenArticle->originalArticle->source_url || $rewrittenArticle->originalArticle->source_name))
                    <div>
                        <p class="block text-sm font-medium text-gray-700 mb-1">
                            Thông tin nguồn bài viết gốc
                        </p>
                        <div class="p-3 bg-gray-50 rounded-md border border-gray-200">
                            @if($rewrittenArticle->originalArticle->source_name)
                            <p class="text-sm text-gray-600">
                                <span class="font-medium">Nguồn:</span> {{ $rewrittenArticle->originalArticle->source_name }}
                            </p>
                            @endif
                            
                            @if($rewrittenArticle->originalArticle->source_url)
                            <div class="flex items-center mt-2">
                                <span class="text-sm text-gray-600 mr-2">Nguồn gốc:</span>
                                <a href="{{ $rewrittenArticle->originalArticle->source_url }}" 
                                   class="text-green-600 hover:text-green-900"
                                   target="_blank" rel="noopener noreferrer" title="Xem nguồn gốc bài viết">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                    </svg>
                                </a>
                            </div>
                            @endif
                        </div>
                    </div>
                    @else
                    @php
                        // Tìm thông tin nguồn gốc từ bài viết gốc (nếu có)
                        $originalArticle = null;
                        if ($rewrittenArticle->originalArticle && $rewrittenArticle->originalArticle->original_article_id) {
                            $originalArticle = \App\Models\Article::find($rewrittenArticle->originalArticle->original_article_id);
                        }
                    @endphp
                    
                    @if($originalArticle && ($originalArticle->source_url || $originalArticle->source_name))
                    <div>
                        <p class="block text-sm font-medium text-gray-700 mb-1">
                            Thông tin nguồn bài viết gốc
                        </p>
                        <div class="p-3 bg-gray-50 rounded-md border border-gray-200">
                            @if($originalArticle->source_name)
                            <p class="text-sm text-gray-600">
                                <span class="font-medium">Nguồn:</span> {{ $originalArticle->source_name }}
                            </p>
                            @endif
                            
                            @if($originalArticle->source_url)
                            <div class="flex items-center mt-2">
                                <span class="text-sm text-gray-600 mr-2">Nguồn gốc:</span>
                                <a href="{{ $originalArticle->source_url }}" 
                                   class="text-green-600 hover:text-green-900"
                                   target="_blank" rel="noopener noreferrer" title="Xem nguồn gốc bài viết">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                    </svg>
                                </a>
                            </div>
                            @endif
                        </div>
                    </div>
                    @endif
                    @endif
                </div>
            </div>
            
            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Ảnh đại diện</h3>
                
                <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                    <div class="sm:col-span-6">
                        @if($rewrittenArticle->featured_image)
                            <div class="mb-4">
                                <p class="mb-2 text-sm text-gray-500">Ảnh hiện tại:</p>
                                <img src="{{ $rewrittenArticle->featured_image_url }}" alt="{{ $rewrittenArticle->title }}" class="max-w-xs h-auto rounded-lg shadow">
                            </div>
                        @endif
                        
                        <label for="featured_image" class="block text-sm font-medium text-gray-700">
                            Tải lên ảnh mới (tùy chọn)
                        </label>
                        <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                            <div class="space-y-1 text-center">
                                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                                <div class="flex text-sm text-gray-600">
                                    <label for="featured_image" class="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
                                        <span>Tải tệp lên</span>
                                        <input id="featured_image" name="featured_image" type="file" class="sr-only">
                                    </label>
                                    <p class="pl-1">hoặc kéo và thả</p>
                                </div>
                                <p class="text-xs text-gray-500">
                                    PNG, JPG, GIF tối đa 2MB
                                </p>
                            </div>
                        </div>
                        @error('featured_image')
                            <p class="mt-2 text-sm text-red-600">{{ $message }}</p>
                        @enderror
                    </div>
                </div>
            </div>

            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Nội dung hiện tại</h3>
                <div class="prose max-w-none mt-2 p-4 bg-gray-50 rounded-md border border-gray-200 text-gray-800">
                    {!! $rewrittenArticle->formatted_content !!}
                </div>
                <p class="mt-3 text-sm text-gray-600">
                    Nội dung này sẽ được gửi tới AI để viết lại. Quá trình này có thể mất vài giây.
                </p>
            </div>

            <div class="border-b border-gray-200 pb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Cấu hình AI</h3>
                
                <div class="bg-gray-50 px-4 py-3 rounded-md">
                    <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                        <div class="sm:col-span-1">
                            <dt class="text-sm font-medium text-gray-500">Nhà cung cấp AI</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ ucfirst($aiSettings->provider) }}</dd>
                        </div>
                        <div class="sm:col-span-1">
                            <dt class="text-sm font-medium text-gray-500">Mô hình</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ $aiSettings->model_name }}</dd>
                        </div>
                        <div class="sm:col-span-1">
                            <dt class="text-sm font-medium text-gray-500">Tự động duyệt</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ $aiSettings->auto_approval ? 'Đã bật' : 'Đã tắt' }}</dd>
                        </div>
                        <div class="sm:col-span-1">
                            <dt class="text-sm font-medium text-gray-500">Giới hạn hàng ngày</dt>
                            <dd class="mt-1 text-sm text-gray-900">{{ $aiSettings->max_daily_rewrites == 0 ? 'Không giới hạn' : $aiSettings->max_daily_rewrites . ' bài viết' }}</dd>
                        </div>
                    </dl>
                    <div class="mt-4">
                        <a href="{{ route('admin.ai-settings.index') }}" class="text-sm font-medium text-blue-600 hover:text-blue-800">
                            Thay đổi cài đặt AI →
                        </a>
                    </div>
                </div>
            </div>

            <div class="flex justify-end">
                <a href="{{ route('admin.rewritten-articles.show', $rewrittenArticle) }}" class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none">
                    Hủy
                </a>
                <button type="submit" class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none">
                    Viết lại bằng AI
                </button>
            </div>
        </form>
    </div>
</div>

@push('scripts')
<script>
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('category_id');
    const subcategorySelect = document.getElementById('subcategory_id');
    
    if (categorySelect && subcategorySelect) {
        categorySelect.addEventListener('change', function() {
            const categoryId = this.value;
            
            // Clear current options
            subcategorySelect.innerHTML = '<option value="">-- Chọn danh mục con --</option>';
            
            // Very important: Clear the selected subcategory value when category changes
            subcategorySelect.value = '';
            
            if (categoryId) {
                // Fetch subcategories for the selected category
                fetch(`/admin/categories/${categoryId}/subcategories`)
                    .then(response => response.json())
                    .then(subcategories => {
                        if (subcategories.length > 0) {
                            subcategories.forEach(subcategory => {
                                const option = document.createElement('option');
                                option.value = subcategory.id;
                                option.textContent = subcategory.name;
                                subcategorySelect.appendChild(option);
                            });
                        }
                    })
                    .catch(error => console.error('Error fetching subcategories:', error));
            }
        });
    }
});
</script>
@endpush
@endsection 